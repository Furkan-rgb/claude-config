#!/usr/bin/env bash
# Prints the open (non-Done) items on this project's local task board,
# so every turn starts with the board's current state in context.
#
# Must never fail the turn: any problem (no board, python3 missing,
# malformed state) results in no output and a clean exit.
set -u

board="${CLAUDE_PROJECT_DIR:-.}/.board"
[ -f "$board/board.json" ] || exit 0
[ -f "$board/board.py" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

out="$(timeout 4 python3 "$board/board.py" list --limit 12 2>/dev/null)" || exit 0
[ -n "$out" ] || exit 0

printf 'Board (open items):\n'
printf '%s\n' "$out"
printf 'Reconcile before acting: any item you start, finish, block, or learn something new about this turn gets its status or a comment updated now \xe2\x80\x94 never later.\n'

exit 0
