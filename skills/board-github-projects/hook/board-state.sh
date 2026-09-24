#!/usr/bin/env bash
# Prints the open (non-Done) items on this project's task board,
# so every turn starts with the board's current state in context.
#
# Must never fail the turn: any problem (gh missing, unauthenticated,
# offline, malformed output) results in no output and a clean exit.
set -u

# The board comes from the shared 60-second cache, not a fresh API call: `commit-msg` wants the
# same answer, and a rebase asking GitHub once per commit earns a secondary rate-limit.
CACHE_SH="$(cd "$(dirname "$0")" && pwd)/board-cache.sh"

command -v python3 >/dev/null 2>&1 || exit 0
[ -x "$CACHE_SH" ] || exit 0

# 0 is fresh and 3 is a stale-but-usable copy; both are worth showing. Anything else has no JSON.
json="$("$CACHE_SH" 2>/dev/null)"; rc=$?
[ "$rc" = "0" ] || [ "$rc" = "3" ] || exit 0
[ -n "$json" ] || exit 0

printf '%s' "$json" | python3 -c '
import json, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

wanted = {"in progress": 0, "next": 1, "blocked": 2}

items = []
for it in data.get("items", []):
    status = it.get("status")
    rank = wanted.get((status or "").lower())
    if rank is None:
        continue
    content = it.get("content", {}) or {}
    title = content.get("title") or it.get("title")
    if not title:
        continue
    number = content.get("number")
    items.append((rank, status, title, number))

if not items:
    sys.exit(0)

items.sort(key=lambda r: r[0])

print("Board (open items):")

for _, status, title, number in items:
    line = f"{status} · {title}"
    if number is not None:
        line += f" (#{number})"
    print(line)

print("Reconcile before acting: any item you start, finish, block, or learn something new about this turn gets its status or a comment updated now — never later.")
' 2>/dev/null

exit 0
