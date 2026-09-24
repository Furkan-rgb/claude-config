#!/usr/bin/env bash
# SessionStart: inject the version-matched Orca orchestration guide into context,
# but only inside an Orca-managed session (ORCA_CLI_COMMAND is exported by Orca).
# Outside Orca this prints {} and does nothing.
set -u

cat >/dev/null 2>&1 || :   # drain the hook's stdin payload

if [ -z "${ORCA_CLI_COMMAND-}" ]; then
  printf '{}\n'
  exit 0
fi

guide=$(sh -c "$ORCA_CLI_COMMAND skills get orchestration" 2>/dev/null) || guide=""

if [ -z "$guide" ]; then
  printf '{}\n'
  exit 0
fi

printf '%s' "$guide" | python3 -c '
import json, sys
guide = sys.stdin.read()
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": (
            "This is an Orca-managed session. The version-matched Orca "
            "orchestration guide follows; use it for any coordination work.\n\n"
            + guide
        ),
    }
}))
'
