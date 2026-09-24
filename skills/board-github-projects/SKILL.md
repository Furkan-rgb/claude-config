---
name: board-github-projects
description: Task board discipline and mechanics for GitHub Projects v2: bootstrap, read, move, comment, close, and the per-turn hook.
---

# Board: GitHub Projects v2

The board is the single source of truth for task state. Prose documents describe how the system
works and record evidence; they never carry a to-do list.

Rules of movement, statuses and WIP limits are defined in the global CLAUDE.md Task Tracking
section; this skill is mechanics only.

## When to load

Detection signal: the repo's `.claude/hooks/board-state.sh` invokes `gh project`.

Load this skill when a project's `AGENTS.md`/`CLAUDE.md` names it as the project's board skill, or
when bootstrapping a tracker for a project that has none and the work spans sessions or has
multiple independently owned milestones. Load it before the first dispatch, not after.

## Discover ids

Never hard-code ids in prose or in a plan; read them fresh each session.

    gh project list --owner <owner> --format json            # project number and PVT_ id
    gh project field-list <N> --owner <owner> --format json  # Status field id + option ids
    gh project item-list <N> --owner <owner> --format json   # item PVTI_ ids + current status

Status field id looks like `PVTSSF_…`; its `options[]` carry the per-status option ids. Item ids
look like `PVTI_…`. The project id (`PVT_…`) comes from `project list`.

## Read

    gh project item-list <N> --owner <owner> --format json --limit 100

Open items are those whose `status` is neither `Done` nor null. An item's content is not always
an issue: a card added straight to the board (`item-create`, or "+ Add item" in the UI) is a
`DraftIssue` and has no `content.number` — only `content.title`. Do not assume `content.number`
exists; read `content.title` (falling back to the item's own `title`) and treat `content.number`
as optional throughout. The per-turn hook prints `<Status> · <title>`, appending ` (#n)` only
when the item is linked to a real issue.

## Move

Over REST, not GraphQL — GraphQL has its own points bucket that has been observed pinned for
hours under concurrent agent load, while REST on the same token kept working:

    gh api "/users/<owner>/projectsV2/<N>/items/<item_id>" -X PATCH \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -F 'fields[][id]=<status_field_id>' -f 'fields[][value]=<option-id>'

`<item_id>` is the REST numeric id (not the `PVTI_…` node id) — read it, along with
`status_field_id` and the option ids, from the 60s cache `board-cache.sh` already maintains
(`.items[].project_item_id`, `.status_field_id`, `.status_options[]` — `{id, name:{raw}}`), or
resolve them fresh with `gh api "/users/<owner>/projectsV2/<N>/fields"` and
`gh api "/users/<owner>/projectsV2/<N>/items?fields[]=<status_field_id>"` (`--paginate`; the list
endpoint has been observed laggy immediately after a write, so prefer a fresh single-item GET —
`/items/<item_id>` — over the list when confirming a move that just happened). `id` in the PATCH
body must be passed with `-F` (numeric), not `-f` (string) — the REST API rejects a quoted field
id. Read back with a fresh single-item GET and report the status you read, never the PATCH's own
response.

## Comment

    gh issue comment <n> --repo <owner>/<repo> --body "…"

Finding comment (when the finding is made, not when it lands) — ≤8 lines, facts and pointers:
what was observed, where (file/symbol/run id), what it changes about the item's plan.

Landing comment — ≤5 lines: merge hash, verification result, experiment-log entry id if any.

## Close

Implementers' commits use a `Refs #n` trailer; the landing merge commit carries `Closes #n`.
If the merge did not close it:

    gh issue close <n> --repo <owner>/<repo>

Close the issue and move the item to Done in the same step — never one without the other.
Retired scope: comment saying why it is retired, then close. Never delete the item.

## Create

    gh issue create --repo <owner>/<repo> --title "…" --body "…"
    gh api "/users/<owner>/projectsV2/<N>/items" -X POST \
      -H "X-GitHub-Api-Version: 2022-11-28" -f type=Issue -F id=<issue database id>
    # then Move, above, to set Status

`id` is the issue's REST **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`), not
its number — pass it with `-F`. A 422 `Content already exists in this project` means it is
already an item; look it up instead of retrying the add.

Titles are done-conditions ("Speed multiplier declared and confirmed from game state"), not topics.
Bodies carry the objective, the done-condition, and pointers to the evidence that will settle it.

A card can also be added to the board directly (`gh project item-create` or "+ Add item" in the
UI) without an issue behind it — a `DraftIssue`. A draft is fine sitting in Backlog or Next; it is
just a to-do line that has not earned an issue yet. **At dispatch — the move to In Progress — it
must become a real issue**, because the landing gate (`commit-msg`) matches commits against
`content.number`, and a draft has none:

    gh repo view <owner>/<repo> --json id   # repositoryId, R_…
    gh api graphql -f query='mutation($item:ID!,$repo:ID!){
      convertProjectV2DraftIssueItemToIssue(input:{itemId:$item, repositoryId:$repo}){
        item{ id content{ ... on Issue { number title } } } } }' \
      -f item=<PVTI_…> -f repo=<R_…>

Read the item back afterward — `content.number` now exists — before moving Status to In Progress.

## Hook

A `UserPromptSubmit` hook injects the open items into every turn, so board state cannot silently
drift. `board-state.sh` never calls `gh` itself — it reads through `board-cache.sh`, a shared,
60-second, per-uid cache file. Two independent readers want the same answer each session
(`board-state.sh` once per turn, and the `commit-msg` landing gate below once per commit and once
per merge), and hitting the GitHub API from both earns a secondary rate-limit — observed
2026-09-20, `gh` reporting it as the unhelpful `unknown owner type`. A rate-limited board gate is
a gate that blocks correct work, which is the failure that gets a guard switched off. The cache
also has an exit-code contract its callers must honour (0 fresh, 3 stale-but-usable, 1 nothing
usable) — see the comment header in `hook/board-cache.sh`.

`board-state.sh` prints ≤15 lines and is fail-safe: missing `gh`/`jq`, no auth, offline, or
malformed output means no output and exit 0 — it must never fail a turn. Needs `gh` authenticated
with the `project` scope (`gh auth refresh -s project`).

`.claude/settings.json` (the command is quoted — an unquoted `$CLAUDE_PROJECT_DIR` path with a
space in it silently fails open, which is exactly the shape of bug this project has already
shipped once, in the staging guard):

    {
      "hooks": {
        "UserPromptSubmit": [
          { "hooks": [ { "type": "command",
                         "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/board-state.sh\"",
                         "timeout": 5 } ] }
        ]
      }
    }

Templates: `hook/board-state.sh` and `hook/board-cache.sh` beside this skill. Copy both to
`.claude/hooks/`, substitute the `<owner>` and `<N>` placeholders (only `board-cache.sh` carries
them — `board-state.sh` delegates), `chmod +x` both.

## Re-brief after compaction

A `UserPromptSubmit` hook only fires on a prompt. Compaction, `/resume`, and session start are
not prompts — a compacted session otherwise loses the board and the handover in the same moment
it loses everything else, which is precisely when both matter most.

A `SessionStart` hook fires on all three (matchers `compact`, `resume`, `startup`) and its stdout
is injected as context the same way `UserPromptSubmit`'s is. Point it at the same
`board-state.sh`, plus the handover's "Current resume point" section if the project keeps one
(Arterial does, in `docs/04-process/state-of-play.md`):

    {
      "hooks": {
        "SessionStart": [
          { "matcher": "compact|resume|startup",
            "hooks": [ { "type": "command",
                         "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/board-state.sh\"",
                         "timeout": 5 } ] }
        ]
      }
    }

To also surface the handover's resume point, extract the section between its heading and the
next `## ` with `awk`:

    awk '
      /^## Current resume point/ { show=1; next }
      /^## / { show=0 }
      show { print }
    ' "$CLAUDE_PROJECT_DIR/docs/04-process/state-of-play.md"

Add that as a second command in the same `SessionStart` hooks array (or append it inside
`board-state.sh` if the project always keeps its resume point at that path). Either way: every
compaction restarts from the board plus the handover, not from nothing.

## Landing gate

`.githooks/commit-msg` + `git config core.hooksPath .githooks` refuses a commit whose message
lacks a `^(Refs|Closes) #n` trailer citing a board item that is **In Progress**. Branches
`wip/*` are exempt — scratch history, rebased before it lands. It fails OPEN (one line on stderr,
exit 0) when `gh` is unreachable, unauthenticated, or the item list comes back empty — a guard
that blocks correct work when the network is down is a guard someone switches off. It fails
CLOSED only on a missing trailer or an answer the board actually gave (item not on the board, or
on the board with the wrong status).

Measured facts, not assumptions, from a fixture repository on git 2.x:

- `git commit` and `git merge` invoke `commit-msg`. `git cherry-pick`, `git revert`, and
  `git rebase` do **not** — git's sequencer writes those commits without running it. Not a hole
  worth plugging: the branch a cherry-picked or reverted commit lands on is merged, and the merge
  is gated.
- `git commit --no-verify` bypasses the hook entirely, same as any git hook.
- Git writes `.git/MERGE_MSG` with no trailing newline. A plain `while read` loop drops a message's
  last line when it has no trailing newline — which is where the trailer lives — so the hook must
  use `while IFS= read -r line || [ -n "$line" ]`, not a bare `while read`. Getting this wrong
  means the hook refuses every `git merge -m "... Refs #n"`, i.e. every landing, which is the one
  commit the gate most needs to see.

Templates: `hook/commit-msg` beside this skill (copy to `.githooks/commit-msg`, `chmod +x`,
substitute `<owner>`/`<N>`) and `hook/board-cache.sh` above, which `commit-msg` reads through by
relative path.

A rule that is only written down does not execute — this one needs a detector, not a comment,
because `.githooks/` hooks are inert *silently* in a fresh clone (`core.hooksPath` unset means
commits simply succeed, nothing goes red). A `make check`-style script must verify, by running
things rather than reading them:

1. **Wiring**: `git config core.hooksPath` is `.githooks`, and `.githooks/commit-msg` is
   executable. Either wrong means every commit in the checkout is ungated.
2. **Refuse**: in a throwaway fixture repo, with the board cache replaced by a fixed file (no
   network — shim `gh` to exit non-zero and fail the whole run if anything calls it), the hook
   refuses a message with no trailer and refuses one citing an item that is not In Progress.
3. **Allow**: in the same fixture it allows a correct trailer, allows anything on `wip/*`, and
   allows a real `git merge --no-ff -m "... Refs #n"` and a message file with no trailing
   newline — the two cases property 2 alone cannot catch, and the two that have actually broken
   here. A hook that refused everything would pass property 2 and block all work.

Reference implementation: this project's `scripts/check-githooks.py`.

## Bootstrap a new project

1. `gh project create --owner <owner> --title "<repo> Task Board"` (then `gh project link <N>
   --owner <owner> --repo <owner>/<repo>` to attach it to the repo).
2. Set the five Status options. `gh` **cannot** edit an existing field's options — there is no
   `field-edit`, and `field-create --single-select-options` only makes a *new* field. Either edit
   the built-in Status options in the UI, or use GraphQL:

        gh api graphql -f query='mutation($f:ID!){ updateProjectV2Field(input:{fieldId:$f,
          singleSelectOptions:[
            {name:"Backlog",color:GRAY,description:""},
            {name:"Next",color:BLUE,description:""},
            {name:"In Progress",color:YELLOW,description:""},
            {name:"Blocked",color:RED,description:""},
            {name:"Done",color:GREEN,description:""}]}){projectV2Field{...on ProjectV2SingleSelectField{id options{id name}}}}}' \
          -f f=<PVTSSF_…>

   The option list replaces the existing one, so pass all five; options passed without an `id` are
   new ones, and items holding a status that disappears lose it — do this before adding items.
   Verify with `field-list`. `commit-msg` and `board-state.sh` compare the "In Progress" status
   case-insensitively, so a project's own option label (e.g. "In progress") need not match this
   casing exactly.
3. Board-layout view: UI only, `gh` cannot create or configure views. Three clicks: open the
   project → view tab ▾ → *Layout: Board*, grouped by Status.
4. Install the per-turn hook and the landing gate:
   - copy `hook/board-cache.sh` and `hook/board-state.sh` to `.claude/hooks/`, substitute
     `<owner>`/`<N>` in `board-cache.sh`, `chmod +x` both, add the `UserPromptSubmit` and
     `SessionStart` stanzas above to `.claude/settings.json`;
   - copy `hook/commit-msg` to `.githooks/commit-msg`, substitute `<owner>`/`<N>`, `chmod +x`,
     then `git config core.hooksPath .githooks`;
   - wire (or adapt) the `check-githooks.py`-style detector into the project's `make check` so a
     regression in either the wiring or the behaviour fails CI instead of failing silently.
5. Write the pointer into the project's `AGENTS.md`:
   "Task board: GitHub Projects #N, owner <owner>, skill `board-github-projects`; its Status
   vocabulary is Backlog, Next, In Progress, Blocked, Done, and open items are injected each turn
   by the hook in `.claude/settings.json`. Every commit cites its board item with a `Refs #n` /
   `Closes #n` trailer; `.githooks/commit-msg` refuses one that does not (branches `wip/*`
   exempt), and `make check` fails if `core.hooksPath` is not `.githooks`. A fresh clone runs
   `git config core.hooksPath .githooks` once."
6. Turn the project's initial specification into issues with done-condition titles (`issue create`
   → `item-add` → set Status), then read the board back once with `item-list`.
