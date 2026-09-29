---
name: task-ledger
description: The project's task board, whatever backend it lives on (a local file or a GitHub Project). Use it to read, create, move, comment on, and close tasks, and to set a board up in a project that has none. The project's `.ledger/config.json` selects the backend.
---

# Task Ledger

All board work goes through one command: `~/.claude/skills/task-ledger/ledger <verb>`. It finds the project by walking up from the working directory to `.ledger/config.json`, and that file decides where the board lives. The rules below hold for every backend.

## Setting up a board

A project has a board once `.ledger/config.json` exists. Run `init` from the project root:

- **Local:** `ledger init local`. The board is `.ledger/ledger.json`; commit it with the code.
- **GitHub Projects:** the project board must exist first, with a single-select `Status` field whose options are exactly Backlog, Next, In progress, Blocked, Done (create it with `gh project create --owner <login> --title <title>` and set the options in the web UI). Then `ledger init github --owner <login> --project <number> --repo <owner>/<repo>`. Init checks that the board is reachable and that the Status options match. Needs `gh` authenticated with the `project` scope.

Any other platform needs a backend added to the `ledger` script first: a class with the same methods as `LocalBackend` plus its own `init`, registered in `BACKENDS`. Do not improvise one inside a project.

To get the board brief in every session, the project registers the hook in its `.claude/settings.json`:

```json
"hooks": {
  "SessionStart": [{"matcher": "startup|resume|compact", "hooks": [{"type": "command", "command": "~/.claude/skills/task-ledger/ledger brief"}]}],
  "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "~/.claude/skills/task-ledger/ledger brief --changes"}]}]
}
```

The first gives the open items at session start and after compaction; the second prints only what changed since, and nothing when nothing did.

## Verbs

- `list [--all] [--json]` open items, In progress first; `--all` includes Done
- `show <n>` one item with its body and comments
- `create --title "<done-condition>" [--body ...] [--status Next]`
- `move <n> <status>`
- `comment <n> --text "..."`
- `close <n> --text "<completion comment>"`
- `board-json` the raw board for commit gates (exit 0 fresh, 3 stale, 1 unavailable)
- `status <n>` one item's status looked up directly, empty when it is not on the board (exit 2 if the lookup failed); commit gates use it for items missing from `board-json`, which can lag a write

Every write reads the status back and prints it; trust that line, not the command's exit alone.

## Rules

- The board is the only record of task state; prose documents describe the system and record evidence, never a to-do list.
- **Statuses:** Backlog (accepted, unordered), Next (committed, top first), In progress (dispatched and owned), Blocked (waiting on a named dependency), Done (done-condition verified). Move an item to In progress when its work is dispatched, to Blocked with a comment naming the dependency, and to Done only by `close`.
- Update the board in the turn the change happens, and report the state read back, never the edit intended.
- **Titles are done-conditions:** a title states what is true when the item is finished, checkable by someone else.
- **Findings** go on the item as a comment of at most 8 lines when they are made, not when the work lands.
- **Close** only after the done-condition is verified, with a completion comment of at most 5 lines that cites the commit hash.
- **Retire, never delete:** an item that is no longer wanted gets a comment saying why and is closed.
- On GitHub, a draft card becomes an issue when it moves to In progress, because commits cite issue numbers.
