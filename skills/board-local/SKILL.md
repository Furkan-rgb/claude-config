---
name: board-local
description: Task board discipline and mechanics for a local JSON board (.board/board.json): bootstrap, read, move, comment, close, and the per-turn hook.
---

# Board: local JSON

The board is the single source of truth for task state. Prose documents describe how the system
works and record evidence; they never carry a to-do list. Here the board is one file in the repo,
`.board/board.json`, driven by `.board/board.py` — no network, no auth, no service.

Rules of movement, statuses and WIP limits are defined in the global CLAUDE.md Task Tracking
section; this skill is mechanics only.

## When to load

Detection signal: `.board/board.json` exists in the repo.

Load this skill when a project's `AGENTS.md`/`CLAUDE.md` names it as the project's board skill, or
when bootstrapping a tracker for a project that has none, the work spans sessions or has multiple
independently owned milestones, and the project is small or fast-moving enough that a repo-local
board beats a hosted one. Load it before the first dispatch, not after.

Migrating to a hosted board later: dump the whole board with `python3 .board/board.py list --all
--json`, create one issue per item from that dump (keeping title, body, comments, status), swap
`.claude/hooks/board-state.sh` for the hosted skill's hook template and the `AGENTS.md` pointer
line for that skill's, then delete `.board/`. Ids change, so no prose may cite them.

## Discover ids

Nothing to discover: the id is the `#n` printed by `list` and `create`, stable for the item's life.
Still read the board fresh each session rather than trusting ids remembered from prose or a plan.

## Read

    python3 .board/board.py list            # open items, ordered Next → In progress → Blocked → Backlog
    python3 .board/board.py list --all      # includes Done
    python3 .board/board.py list --json     # full records, for machines
    python3 .board/board.py show <n>        # one item with body and comments

`list` prints `#id [Status] title`, at most 14 lines, with a trailing `...and N more` when the
board is longer.

## Move

    python3 .board/board.py move <n> "In progress"

The status name is validated against the five statuses (Backlog, Next, In progress, Blocked, Done);
an unknown status or unknown id exits 1 with a message. `move` prints the item as re-read from
`board.json` after the write — report that line, never the intention behind the edit.

## Comment

    python3 .board/board.py comment <n> --text "…"

Finding comment (when the finding is made, not when it lands) — ≤8 lines, facts and pointers:
what was observed, where (file/symbol/run id), what it changes about the item's plan.

Completion comment — ≤5 lines: commit or merge hash when applicable, verification result, and
experiment-log entry id if any.

## Close

    python3 .board/board.py close <n> --text "landed abc1234; <verification>"

`close` appends the optional comment and sets Done, then reads the item back. Close only when the
item's done-condition has been verified. For code work, cite the commit or merge hash; include
`Closes #n` in the landing commit message for traceability. Commit the board update with the
landing when practical. For a measurement or other non-code item, record the result instead.

Retired scope: comment saying why it is retired, then `close`. Never delete the item.

## Create

    python3 .board/board.py create --title "…" --body "…" --status Backlog

Prints the new `#id`. Titles are done-conditions ("Speed multiplier declared and confirmed from
game state"), not topics. Bodies carry the objective, the done-condition, and pointers to the
evidence that will settle it.

## Hook

A `UserPromptSubmit` hook injects the open items into every turn. A `SessionStart` hook restores
them after startup, resume, or compaction. The script prints ≤15 lines and is fail-safe: no
`.board/board.json`, no `python3`, or malformed state means no output and exit 0.

`.claude/settings.json`:

    {
      "hooks": {
        "UserPromptSubmit": [
          { "hooks": [ { "type": "command",
                         "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/board-state.sh\"",
                         "timeout": 5 } ] }
        ],
        "SessionStart": [
          { "matcher": "startup|resume|compact",
            "hooks": [ { "type": "command",
                         "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/board-state.sh\"",
                         "timeout": 5 } ] }
        ]
      }
    }

Template: `hook/board-state.sh` beside this skill; copy it to `.claude/hooks/board-state.sh`
unedited — it has no placeholders.

## Bootstrap a new project

1. `mkdir -p .board` and copy `board.py` from this skill to `.board/board.py` (`chmod +x`). The
   project keeps its own copy so the repo is self-contained and the skill path is not a runtime
   dependency; the skill directory is the template, not the installation.
2. `python3 .board/board.py init` — writes `{"next_id": 1, "items": []}` to `.board/board.json`.
3. Install the hook: copy `hook/board-state.sh` to `.claude/hooks/board-state.sh`, `chmod +x`, add
   the `settings.json` stanza above.
4. Write the pointer into the project's `AGENTS.md`:
   "Task board: local, `.board/board.json`, skill `board-local`; hook in `.claude/settings.json`."
5. Turn the project's initial specification into items with done-condition titles (`create`, then
   `move` the committed ones to Next), then read the board back once with `list`.
