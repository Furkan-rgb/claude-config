import { expect, mock, test } from 'claude-code/testing'

import type { Roadmap } from '../types'

const GOALS: Roadmap['goals'] = [
    { title: 'M1 Movement works', exits: [{ ref: '1', title: 'Hex grid draws', done: true }] },
    { title: 'M2 Combat loop playable', exits: [
      { ref: '2', title: 'Attacks resolve', done: true },
      { ref: '3', title: 'Enemies act', done: false },
    ] },
    { title: 'M3 Save and load', exits: [] },
]

const RECORDS = [
  { id: 'ADR-0001', title: 'Tiles are hexes', status: 'accepted', blocks: null, path: 'docs/decisions/0001-hexes.md' },
  { id: 'ADR-0002', title: 'Combat runs in real time?', status: 'proposed', blocks: 'M2 enemy turns', path: 'docs/decisions/0002-combat.md' },
]

const ran = (stdout: string) => ({ value: { exitCode: 0, stdout, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } })

test('the pane shows the current goal, the rest, and the Proposed records as open questions', async ($, on) => {
  // The world beneath the plugin: `ledger progress --json` and `decisions index --json`.
  on('env.get', () => ({ value: '/home/test' }))
  on('process.run', (_$, e) => ran(JSON.stringify(e.argv[0]!.endsWith('/ledger') ? GOALS : RECORDS)))
  on('fs.exists', () => ({ value: true }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  await $.command.run({ command: 'roadmap', args: '', origin: { kind: 'composer' },
                        presentation: { isFullscreen: true, columns: 160 } })
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({
      plugin: 'roadmap', surface, component: 'Pane', requestId: 'roadmap',
      props: { title: 'Roadmap', isFocused: false, bodyColumns: 50, placement: 'dock',
               scroll: { offset: 0, bodyRows: 30 }, view: {} },
    })
    expect(await ui.find({ text: /▶ M2 Combat loop playable {2}1\/2/ })).toBeDefined()
    expect(await ui.find({ text: /\[ \] #3 Enemies act/ })).toBeDefined()
    expect(await ui.find({ text: /· M3 Save and load {2}0\/0/ })).toBeDefined()
    expect(await ui.find({ text: /1 complete, awaiting reconcile/ })).toBeDefined()
    expect(await ui.find({ text: /▶ M1/ })).toBeUndefined()
    expect(await ui.find({ text: /ADR-0002 Combat runs in real time\?/ })).toBeDefined()
    expect(await ui.find({ text: /blocks: M2 enemy turns/ })).toBeDefined()
    expect(await ui.find({ text: /ADR-0001/ })).toBeUndefined()
  }
})

test('the session starts without waiting for the board', async ($, on) => {
  // The board answers 20 s late, as a GitHub board does; the session must be under way before.
  const clock = mock.clock(on)
  let answered = 0
  on('env.get', () => ({ value: '/home/test' }))
  on('process.run', async () => {
    await clock.sleep(20_000)
    answered++
    return ran('')
  })
  on('fs.exists', () => ({ value: false }))
  on('command.register', () => ({ value: { command: 'roadmap' } }))
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/home/test/project', surface: 'terminal', isInteractive: true })
  expect(answered).toBe(0)
  await clock.advance(20_000)
  expect(answered).toBe(2)
})

test('a project without decision records shows no open-questions section', async ($, on) => {
  on('env.get', () => ({ value: '/home/test' }))
  on('process.run', (_$, e) => ran(e.argv[0]!.endsWith('/ledger') ? JSON.stringify(GOALS) : ''))
  on('fs.exists', () => ({ value: true }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  await $.command.run({ command: 'roadmap', args: '', origin: { kind: 'composer' },
                        presentation: { isFullscreen: true, columns: 160 } })
  const ui = await $.ui.mount({
    plugin: 'roadmap', surface: 'terminal', component: 'Pane', requestId: 'roadmap',
    props: { title: 'Roadmap', isFocused: false, bodyColumns: 50, placement: 'dock',
             scroll: { offset: 0, bodyRows: 30 }, view: {} },
  })
  expect(await ui.find({ text: /▶ M2/ })).toBeDefined()
  expect(await ui.find({ text: /Open questions/ })).toBeUndefined()
})
