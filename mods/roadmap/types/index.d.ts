export type Exit = { ref: string; title: string; done: boolean }
export type Goal = { title: string; exits: Exit[] }
/** A Proposed decision record: an open question, and what waits on it. */
export type OpenQuestion = { id: string; title: string; blocks: string | null }

/** What the pane draws: the board's open goals in roadmap order and the open questions, each
 * null when the project has no board or no decision records; `problem` says why a read failed. */
export type Roadmap = { goals: Goal[] | null; open: OpenQuestion[] | null; problem: string | null; readAt: string }

declare module 'claude-code' {
  interface PluginState {
    roadmap: { view: Roadmap }
  }
}
