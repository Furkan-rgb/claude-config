# Claude Code config

My global Claude Code setup: the Lead and its workers (`agents/`), the Lead's playbook with decision records (`skills/lead-playbook/`), the task board (`skills/task-ledger/`), the roadmap pane (`mods/roadmap/`), settings, status line and themes. Only hand-maintained config is tracked (see `.gitignore`); everything else in `~/.claude` is runtime state.

## Needs

- Claude Code 2.1.287 or later (the roadmap pane is a mod)
- `python3` (standard library only) for `ledger`, `decisions` and the status line
- `gh`, authenticated with the `project` scope, for GitHub-backed boards: `gh auth login --scopes project`

## Install on a new machine

With no `~/.claude` yet:

```sh
git clone https://github.com/Furkan-rgb/claude-config.git ~/.claude
```

With an existing `~/.claude` (Claude Code already run once); this replaces its tracked files, such as `settings.json`, and keeps the runtime state:

```sh
cd ~/.claude
git init
git remote add origin https://github.com/Furkan-rgb/claude-config.git
git fetch origin
git reset --hard origin/master
git branch -u origin/master
```

Then enable the pre-commit check, which refuses a commit while `./test` fails:

```sh
git -C ~/.claude config core.hooksPath .githooks
```

Then start a new Claude Code session. The roadmap pane and the decisions index load from `settings.json`.

## Tests

`./test` runs every check, in about half a minute:
- the `ledger` and `decisions` scripts against a throwaway local board (`tests/`);
- the settings: every hook command, the status line, the plugin folders and the theme exist;
- each mod's validation, type-check and tests.

Not covered: the ledger's GitHub backend, which needs the network, and how the pane looks on screen.

## Per project

- **Task board:** in the project root, run `~/.claude/skills/task-ledger/ledger init local` or `ledger init github …`. Then add the brief hooks to the project's `.claude/settings.json` (see `skills/task-ledger/SKILL.md`).
- **Decision records:** run `~/.claude/skills/lead-playbook/decisions new "<title>"`, which creates `docs/decisions/`.

## Not in this repo

- `settings.local.json`: this machine's own permissions.
- Skills synced from claude.ai (`skills/synced/`): they arrive with the account.
- Per-project memory (`projects/*/memory/`): it is keyed by each project's absolute path.
