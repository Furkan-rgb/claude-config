import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Goal, OpenQuestion, Roadmap } from '../types'

// The pane is a view: the board (`ledger progress --json`) and the decision records
// (`decisions index --json`) are the sources of truth, read again whenever this session may
// have changed them.

const PANE = 'roadmap'
const RECORDS = 'docs/decisions'
const view = atom({ plugin: 'roadmap', key: 'view' } as const, { goals: null, open: null, problem: null, readAt: '' })

type Read<T> = { value: T | null; problem: string | null }

/** Runs one of the workflow's scripts for its JSON; null with no problem when the project
 * simply has nothing for it (no output, or the script's own `absent` message). */
async function readJson<T>($: EngineInterface, script: string, args: string[], absent?: string): Promise<Read<T>> {
  const home = await $.env.get('HOME')
  const name = script.split('/').pop()
  try {
    const ran = await $.process.run([`${home}/.claude/skills/${script}`, ...args], { timeoutMs: 60_000 })
    if (ran.exitCode === 0) return { value: ran.stdout.trim() ? JSON.parse(ran.stdout) : null, problem: null }
    if (absent && ran.stderr.includes(absent)) return { value: null, problem: null }
    return { value: null, problem: `${name}: ${ran.stderr.trim().slice(0, 200)}` }
  } catch (err) {
    return { value: null, problem: `${name} did not run: ${String(err).slice(0, 200)}` }
  }
}

async function refresh($: EngineInterface) {
  const [goals, records] = await Promise.all([
    readJson<Goal[]>($, 'task-ledger/ledger', ['progress', '--json'], 'no .ledger/config.json'),
    readJson<(OpenQuestion & { status: string })[]>($, 'lead-playbook/decisions', ['index', '--json']),
  ])
  const open = records.value && records.value.filter(r => r.status === 'proposed')
  const problem = [goals.problem, records.problem].filter(Boolean).join('\n') || null
  const readAt = new Date().toTimeString().slice(0, 5)
  await update($, view, (): Roadmap => ({ goals: goals.value, open, problem, readAt }))
}

const isComplete = (g: Goal) => g.exits.length > 0 && g.exits.every(x => x.done)
const count = (g: Goal) => `${g.exits.filter(x => x.done).length}/${g.exits.length}`
const touchesRecords = (path: string) => path.includes(`${RECORDS}/`)

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'roadmap', description: 'Show the roadmap and open questions in a pane' })
    // Not awaited: a GitHub board takes seconds to read, and the session must not wait for it.
    void refresh($)
    // Board changes made outside this session (another session, the GitHub web UI).
    $.clock.every(5 * 60_000, () => void refresh($))
    if ((await $.fs.exists('.ledger/config.json')) || (await $.fs.exists(RECORDS))) {
      void $.ui.open({ id: PANE, title: 'Roadmap' })
    }
    return next(e)
  })

  on('command.run', { command: 'roadmap' }, async $ => {
    await refresh($)
    const opened = await $.ui.open({ id: PANE, title: 'Roadmap' })
    return { text: opened.isPlaced ? 'Roadmap pane opened.' : 'Roadmap pane is waiting for a wider terminal.' }
  })

  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const ran = await next(e)
    if (/\b(ledger|decisions)\b/.test(e.command) || touchesRecords(e.command)) await refresh($)
    return ran
  })

  on('tool.call', { tool: 'Edit' }, async ($, e, next) => {
    const ran = await next(e)
    if (touchesRecords(e.file_path)) await refresh($)
    return ran
  })

  on('tool.call', { tool: 'Write' }, async ($, e, next) => {
    const ran = await next(e)
    if (touchesRecords(e.file_path)) await refresh($)
    return ran
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const { goals, open, problem, readAt } = await read($, view)
    const current = goals?.find(g => !isComplete(g))
    const later = goals?.filter(g => g !== current && !isComplete(g)) ?? []
    const finished = goals?.filter(g => isComplete(g)) ?? []

    return (
      <Box flexDirection="column">
        {problem && <Text color="red" wrap="wrap">{problem}</Text>}
        {goals === null && !problem && <Text dimColor>No task board in this project.</Text>}
        {goals !== null && !current && <Text dimColor>No open goal. Shape the next one with the Lead.</Text>}
        {current && (
          <Box flexDirection="column" marginBottom={1}>
            <Text bold wrap="wrap">▶ {current.title}  {count(current)}</Text>
            {current.exits.map(x => (
              <Text dimColor={x.done} wrap="truncate-end">  {x.done ? '[x]' : '[ ]'} #{x.ref} {x.title}</Text>
            ))}
          </Box>
        )}
        {later.length > 0 && (
          <Box flexDirection="column" marginBottom={1}>
            <Text bold>Then</Text>
            {later.map(g => <Text wrap="truncate-end">  · {g.title}  {count(g)}</Text>)}
          </Box>
        )}
        {finished.length > 0 && <Text dimColor>{finished.length} complete, awaiting reconcile</Text>}
        {open !== null && (
          <Box flexDirection="column" marginTop={1} marginBottom={1}>
            <Text bold>Open questions</Text>
            {open.length === 0 && <Text dimColor>None.</Text>}
            {open.map(q => (
              <Box flexDirection="column">
                <Text wrap="wrap">  {q.id} {q.title}</Text>
                {q.blocks && <Text dimColor wrap="truncate-end">    blocks: {q.blocks}</Text>}
              </Box>
            ))}
          </Box>
        )}
        <Box flexDirection="row" gap={1}>
          <Button hotkey="r" onPress={() => void refresh($)}>Refresh</Button>
          <Text dimColor>{readAt && `read ${readAt}`}</Text>
        </Box>
      </Box>
    )
  })
}
