"""Status-line badge: main agent model/effort + running subagents."""
import json, os, re, sys

AGENTS_DIR = os.path.expanduser("~/.claude/agents")


def agent_defaults(name):
    """model/effort declared in ~/.claude/agents/<name>.md frontmatter."""
    path = os.path.join(AGENTS_DIR, f"{name}.md")
    out = {}
    try:
        with open(path, errors="ignore") as fh:
            for line in fh.read().split("---")[1].splitlines():
                m = re.match(r"\s*(model|effort)\s*:\s*(\S+)", line)
                if m:
                    out[m.group(1)] = m.group(2)
    except Exception:
        pass
    return out


def running_subagents(transcript_path, limit=600):
    """Agent tool calls with no tool_result yet, newest last."""
    try:
        with open(transcript_path, errors="ignore") as fh:
            lines = fh.readlines()[-limit:]
    except Exception:
        return []
    spawned, finished = {}, set()
    for line in lines:
        try:
            rec = json.loads(line)
        except Exception:
            continue
        content = rec.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") in ("Agent", "Task"):
                inp = block.get("input") or {}
                spawned[block["id"]] = {
                    "type": inp.get("subagent_type") or "claude",
                    "model": inp.get("model"),
                }
            elif block.get("type") == "tool_result":
                finished.add(block.get("tool_use_id"))
    return [v for k, v in spawned.items() if k not in finished]


def short_model(model_id):
    for name in ("opus", "sonnet", "haiku", "fable"):
        if name in (model_id or "").lower():
            return name
    return (model_id or "?").split("-")[0]


def main():
    try:
        p = json.load(sys.stdin)
    except Exception:
        return
    model = p.get("model", {})
    main_model = short_model(model.get("id"))
    main_effort = (p.get("effort") or {}).get("level", "?")
    parts = [f"◆ {main_model}·{main_effort}"]

    subs = running_subagents(p.get("transcript_path", ""))
    if subs:
        rendered = []
        for sub in subs:
            d = agent_defaults(sub["type"])
            m = short_model(sub["model"]) if sub["model"] else d.get("model", main_model)
            e = d.get("effort", main_effort)
            rendered.append(f"{sub['type']}:{m}·{e}")
        parts.append("⇢ " + ", ".join(rendered))

    ctx = p.get("context_window", {}).get("used_percentage")
    if ctx is not None:
        parts.append(f"{ctx}% ctx")
    print("  │  ".join(parts))


main()
