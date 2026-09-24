#!/bin/sh
# Renders "model · effort" for this session and any running subagents into the
# Claude Code status line, which Orca displays in the pane.
# Also forwards the payload to Orca's own statusline collector (unchanged behavior).
payload=$({ command -p cat 2>/dev/null || cat; })
[ -n "$payload" ] || exit 0
printf '%s' "$payload" | sh "$HOME/.orca/agent-hooks/claude-statusline.sh" >/dev/null 2>&1 || :
printf '%s' "$payload" | python3 "$HOME/.claude/orca-agent-badge.py" 2>/dev/null || :
