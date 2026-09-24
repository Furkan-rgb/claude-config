#!/usr/bin/env python3
"""Local task board: one JSON file, five statuses, no network.
Lives at .board/board.py in the project it serves; state is .board/board.json
beside it. Run as `python3 .board/board.py <verb>` from the project root."""
import argparse, json, os, sys, tempfile
from datetime import datetime, timezone

STATUSES = ["Backlog", "Next", "In progress", "Blocked", "Done"]
ORDER = {"Next": 0, "In progress": 1, "Blocked": 2, "Backlog": 3, "Done": 4}
MAX_LINES = 14  # 13 items + "...and N more"; the hook adds one header line

def path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "board.json")

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def load():
    try:
        with open(path()) as fh:
            return json.load(fh)
    except FileNotFoundError:
        die(f"no board at {path()} - run `board.py init` first")
    except json.JSONDecodeError as exc:
        die(f"{path()} is not valid JSON: {exc}")

def save(board):
    d = os.path.dirname(path())
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".board.", suffix=".json")
    with os.fdopen(fd, "w") as fh:
        json.dump(board, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path())

def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def find(board, item_id):
    for item in board["items"]:
        if item["id"] == item_id:
            return item
    die(f"no item #{item_id} on the board")

def check_status(name):
    if name not in STATUSES:
        die(f"unknown status {name!r}; one of: " + ", ".join(STATUSES))
    return name

def line(item):
    return f"#{item['id']} [{item['status']}] {item['title']}"

def read_back(item_id):
    """Report an item as the file has it, never as we wrote it."""
    print(line(find(load(), item_id)))

def cmd_init(args):
    if os.path.exists(path()):
        die(f"board already exists at {path()}")
    save({"next_id": 1, "items": []})
    print(f"initialised {path()}")

def cmd_list(args):
    board = load()
    items = [i for i in board["items"] if args.all or i["status"] != "Done"]
    items.sort(key=lambda i: (ORDER[i["status"]], i["id"]))
    if args.json:
        print(json.dumps(items, indent=2))
        return
    if not items:
        return
    cap = args.limit
    if len(items) > cap:
        shown, rest = items[: cap - 1], len(items) - (cap - 1)
    else:
        shown, rest = items, 0
    for item in shown:
        print(line(item))
    if rest:
        print(f"...and {rest} more")

def cmd_create(args):
    board = load()
    item = {"id": board["next_id"], "title": args.title, "body": args.body,
            "status": check_status(args.status), "created": now(),
            "updated": now(), "comments": []}
    board["next_id"] += 1
    board["items"].append(item)
    save(board)
    print(f"#{item['id']}")

def cmd_move(args):
    board = load()
    item = find(board, args.id)
    item["status"] = check_status(args.status)
    item["updated"] = now()
    save(board)
    read_back(args.id)

def cmd_comment(args):
    board = load()
    item = find(board, args.id)
    item["comments"].append({"at": now(), "text": args.text})
    item["updated"] = now()
    save(board)
    print(f"#{item['id']} commented")

def cmd_close(args):
    board = load()
    item = find(board, args.id)
    if args.text:
        item["comments"].append({"at": now(), "text": args.text})
    item["status"] = "Done"
    item["updated"] = now()
    save(board)
    read_back(args.id)

def cmd_show(args):
    item = find(load(), args.id)
    print(line(item))
    print(f"created {item['created']}  updated {item['updated']}")
    if item["body"]:
        print(item["body"])
    for c in item["comments"]:
        print(f"- {c['at']}: {c['text']}")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="verb", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    s = sub.add_parser("list"); s.set_defaults(fn=cmd_list)
    s.add_argument("--all", action="store_true"); s.add_argument("--json", action="store_true")
    s.add_argument("--limit", type=int, default=MAX_LINES - 1)
    s = sub.add_parser("create"); s.set_defaults(fn=cmd_create)
    s.add_argument("--title", required=True); s.add_argument("--body", default="")
    s.add_argument("--status", default="Backlog")
    s = sub.add_parser("move"); s.set_defaults(fn=cmd_move)
    s.add_argument("id", type=int); s.add_argument("status")
    s = sub.add_parser("comment"); s.set_defaults(fn=cmd_comment)
    s.add_argument("id", type=int); s.add_argument("--text", required=True)
    s = sub.add_parser("close"); s.set_defaults(fn=cmd_close)
    s.add_argument("id", type=int); s.add_argument("--text", default="")
    s = sub.add_parser("show"); s.set_defaults(fn=cmd_show)
    s.add_argument("id", type=int)
    args = p.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()
