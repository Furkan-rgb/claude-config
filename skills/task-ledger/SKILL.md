---
name: task-ledger
description: The project's task board, whatever backend it lives on (a local file or a GitHub Project). Use it to read, create, move, comment on, and close tasks, and to set a board up in a project that has none. The project's `.ledger/config.json` selects the backend.
---

# Task Ledger

All board work goes through one command: `~/.claude/skills/task-ledger/ledger <verb>`. It finds the project by walking up from the working directory to `.ledger/config.json`, and that file decides where the board lives. The rules below hold for every backend.

## Setting up a board

A project has a board once `.ledger/config.json` exists. Run `init` from the project root:

- **Local:** `ledger init local`. The board is `.ledger/ledger.json`; commit it with the code.
- **GitHub Projects:** the project board must exist first, with a single-select `Status` field whose options are exactly Backlog, Next, In progress, Blocked, Done (create it with `gh project create --owner <login> --title <title>` and set the options in the web UI). Then `ledger init github --owner <login> --project <number> --repo <owner>/<repo>`. Init checks that the board is reachable and that the Status options match. Needs `gh` authenticated with the `project` scope. The owner also turns on the project's built-in "Item closed" workflow (Workflows → Item closed → Status: Done), so an issue closed by a `Closes #n` commit reaches Done with nobody involved.

To get the board brief in every session, the project registers the hook in its `.claude/settings.json`:

```json
"hooks": {
  "SessionStart": [{"matcher": "startup|resume|compact", "hooks": [{"type": "command", "command": "~/.claude/skills/task-ledger/ledger brief"}]}],
  "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "~/.claude/skills/task-ledger/ledger brief --changes"}]}]
}
```

The first gives the open items at session start and after compaction; the second prints only what changed since, and nothing when nothing did. Both also print, every time until each is dealt with, the cards waiting on a decision and the In progress cards with no live worker (see Workers).

## Workers

The global settings register `ledger hook` on PreToolUse and PostToolUse for `Agent`, SubagentStart, SubagentStop and Stop; it does nothing in a project without a board. It records which worker holds which card, in one file per board outside the repo, shared by every checkout of that board:

- **Dispatch:** every Agent prompt carries a line `Board: #<n>` naming the card the worker serves, or `Board: none`; a prompt with neither is refused. A `Board: #<n>` dispatch records the worker against the card and moves the card to In progress unless it is already there or Done.
- **Claim:** `ledger claim <n> <worker-id>` records a running worker the dispatch did not, such as one started before these hooks or with `Board: none`; the id is the agentId its launch returned.
- **Stop:** when the worker stops, or the Claude session that started it is gone, the card is **waiting on a decision**. Any `move`, `comment` or `close` on the card is that decision; so is dispatching another worker for it. A worker resumed with SendMessage is live again.
- **Turn end:** while a card this session dispatched waits on a decision, the turn's first attempt to end is blocked with `#<n>: its worker stopped`.
- **Brief:** `Waiting on a decision: …` and `In progress with no live worker: …` print on every brief until each card is moved, commented on, closed or re-dispatched.

## Board audit

A board drifts: items done but open, titles and premises overtaken, duplicates. An audit is due when `audit_every_closes` items (in `.ledger/config.json`, default 10) have closed since the last audit card closed, or at once when a milestone exit closes; closes by `Closes #n` commits count too. While one is due and no audit card is In progress, every brief prints `Board audit due (<reason>)` and the first attempt to end each turn is blocked, in every session on the board.

To run it, create a card titled `Board audit: <date>` and dispatch a scout for it with `Board: #<n>` and the checklist below; it is a card like any other, so the hooks move it to In progress and flag it when the scout stops. Apply the verdicts you accept, then close the card with a completion comment naming what was applied; that resets the count. Audit cards need no milestone.

The checklist, pasted into the scout's prompt:

> Audit the board. Scope: every open item of the current milestone (`ledger progress <milestone>`), and every In progress item with no live worker (the brief lists them). For each item give one verdict: done-but-open, title stale, premise stale, duplicate, obsolete, or ok; one line of evidence (a commit, a `file:line`, or the contradicting item); and an action (close, retire, replace, re-parent, comment).
> - Read the remote default branch, never the checkout: `git fetch`, then `git show origin/<default>:<path>`.
> - Use read-only `ledger` verbs only (`list`, `show`, `progress`, `status`); make no repository or board writes.
> - Open every item with `ledger show` and read its last comments. A thin audit is a failure.

## Verbs

- `list [--all] [--json] [--limit N]` open items, In progress first, 20 rows unless `--limit`; `--all` includes Done
- `show <n>` one item with its body and comments
- `create --title "<done-condition>" [--body ...] [--status Next]`
- `move <n> <status>`
- `comment <n> --text "..."`
- `claim <n> <worker-id>` record a running worker against a card (see Workers)
- `close <n> --text "<completion comment>"`; when the item was the last open exit of its milestone, it also prints `Goal complete: <title>`, the cue to reconcile before the next goal
- `board-json` the raw board for commit gates (exit 0 fresh, 3 stale, 1 unavailable)
- `status <n>` one item's status looked up directly, empty when it is not on the board (exit 2 if the lookup failed); commit gates use it for items missing from `board-json`, which can lag a write
- `milestone list` each milestone with its open/closed item counts and due state
- `milestone create --title "<title>" [--description ...]`
- `milestone rename <milestone> --title "<new title>"` retitle a milestone; renumbering its `M<n>` prefix re-orders the roadmap
- `milestone set <n> <milestone>` assign an item to a milestone, named by its title or a unique prefix (`M3`); a draft card becomes an issue first
- `parent <child> <parent> [--dry-run]` make an item a sub-item of another (GitHub sub-issues; replaces any existing parent); `--dry-run` prints the API call instead of making it
- `unparent <child> [--dry-run]` remove an item from its parent
- `progress [<milestone>]` the tree milestone → exits → tasks with done/total at each level, computed from item states; open milestones unless one is named, in roadmap order; `--json` prints the same tree as JSON

When the project has open milestones, the session-start `brief` is sized by the current goal, not the board. It opens with `Milestones: ▶ M3 9/24 exits · M4 3/45 exits`, the arrow marking the current goal (the first not yet complete). Then come `Current goal: <title>` with that goal's open exits and their status, an `Unplaced:` line for open items with neither a milestone nor a parent, the work in progress anywhere else, and a `Not shown:` count of the remaining Next and Blocked items. `ledger list` shows those. A board without milestones is briefed as its In progress and Next items.

Every write reads the status back and prints it; trust that line, not the command's exit alone. "status unconfirmed" means the write went through: check with `ledger status <n>`, never repeat the write.

## Rules

- The board is the only record of task state; prose documents describe the system and record evidence, never a to-do list.
- **Statuses:** Backlog (accepted, unordered), Next (committed, top first), In progress (dispatched and owned), Blocked (waiting on a named dependency), Done (done-condition verified). An item moves to In progress when a worker is dispatched with `Board: #<n>` (the hook moves it), or when you take it yourself; move it to Blocked with a comment naming the dependency, and to Done only by `close`.
- Update the board in the turn the change happens, and report the state read back, never the edit intended.
- **Titles are done-conditions:** a title states what is true when the item is finished, checkable by someone else.
- **Findings** go on the item as a comment of at most 8 lines when they are made, not when the work lands.
- **Close** only after the done-condition is verified, with a completion comment of at most 5 lines that cites the commit hash.
- **Retire, never delete:** an item that is no longer wanted gets a comment saying why and is closed.
- On GitHub, a draft card becomes an issue when it moves to In progress, because commits cite issue numbers.
- **Milestones:** every open item belongs to one milestone exit; exits are parent issues; status is computed, never hand-written. An exit is an item in a milestone with no parent; its tasks are its sub-items.
- **Goals:** a milestone is a goal, an outcome derived from the project's decision records, not a bucket; the roadmap is the order of milestones, set by their `M<n>` title prefix. A milestone's description begins with a `Serves:` line naming the records it derives from (`Serves: ADR-0013, ADR-0020`). A task has one parent; one serving two goals is shared groundwork, its own item under the earlier goal. When a design decision changes, find the goals that traced to it by their `Serves:` lines and re-point or retire them and their items.
- Only the Lead writes to the board, so it has one writer; workers report to the Lead.
