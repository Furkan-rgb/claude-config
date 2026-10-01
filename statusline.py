#!/usr/bin/env python3
"""Status line: model and effort, context use, and subscription usage against pace.

Pace is the share of a usage window that has elapsed: at pace, usage runs out
exactly when the window resets. Each window shows a bar filled to its usage,
with a marker at pace. Usage is green at or under pace, yellow up to 10 points
over, red beyond that. The countdown is the time left until the window resets.
"""
import json
import sys
import time

GREEN, YELLOW, RED, DIM, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"
WINDOWS = (("5h", "five_hour", 5 * 3600), ("week", "seven_day", 7 * 86400))
BAR_WIDTH = 10


def bar(used, pace, colour):
    filled = min(BAR_WIDTH, round(used / 100 * BAR_WIDTH))
    marker = round(pace / 100 * BAR_WIDTH)
    cells = [f"{colour}█{RESET}" if i < filled else f"{DIM}░{RESET}" for i in range(BAR_WIDTH)]
    cells.insert(marker, "┃")
    return "".join(cells)


def countdown(seconds):
    minutes = max(0, int(seconds // 60))
    days, minutes = divmod(minutes, 1440)
    hours, minutes = divmod(minutes, 60)
    return f"{days}d{hours}h" if days else f"{hours}h{minutes:02d}m" if hours else f"{minutes}m"


def window(label, limit, length):
    used = limit.get("used_percentage")
    resets_at = limit.get("resets_at")
    if used is None or resets_at is None:
        return None
    left = resets_at - time.time()
    pace = min(100, max(0, 100 * (1 - left / length)))
    colour = GREEN if used <= pace else YELLOW if used <= pace + 10 else RED
    return f"{label} {bar(used, pace, colour)} {colour}{used:.0f}%{RESET} {DIM}↻ {countdown(left)}{RESET}"


data = json.load(sys.stdin)
model = data.get("model", {}).get("display_name", "?")
effort = (data.get("effort") or {}).get("level")
parts = [f"{model} {DIM}{effort}{RESET}" if effort else model]
context = (data.get("context_window") or {}).get("used_percentage")
if context is not None:
    parts.append(f"ctx {context:.0f}%")
limits = data.get("rate_limits") or {}
for label, key, length in WINDOWS:
    if key in limits:
        part = window(label, limits[key], length)
        if part:
            parts.append(part)
print(" │ ".join(parts))
