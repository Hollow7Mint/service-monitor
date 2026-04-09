import argparse
import json
import logging
import sys
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def _table(rows: list[dict], cols: Optional[list[str]] = None) -> None:
    if not rows:
        print("(empty)")
        return
    cols = cols or list(rows[0].keys())
    widths = {c: max(len(c), max(len(str(r.get(c, ""))) for r in rows))
              for c in cols}
    sep = "  "
    print(sep.join(c.ljust(widths[c]) for c in cols))
    print("-" * (sum(widths.values()) + len(sep) * (len(cols) - 1)))
    for row in rows:
        print(sep.join(str(row.get(c, "")).ljust(widths[c]) for c in cols))


def cmd_list(args: argparse.Namespace) -> int:
    logger.debug("list: page=%d size=%d", args.page, args.size)
    print(f"Listing (page={args.page} size={args.size})")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    logger.debug("add: name=%s tags=%s", args.name, args.tags)
    print(f"Added: {args.name!r}")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    if not args.yes:
        confirm = input(f"Delete {args.id}? [y/N] ")
        if confirm.lower() != "y":
            print("Aborted.")
            return 0
    print(f"Deleted: {args.id}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    print(f"Record: {args.id}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    print(f"Exported as {args.format} to {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="app",
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--json", dest="as_json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list")
    ls.add_argument("--page", type=int, default=1)
    ls.add_argument("--size", type=int, default=20)
    ls.set_defaults(func=cmd_list)

    add = sub.add_parser("add")
    add.add_argument("name")
    add.add_argument("--tag", action="append", dest="tags", default=[])
    add.set_defaults(func=cmd_add)

    rm = sub.add_parser("delete")
    rm.add_argument("id")
    rm.add_argument("-y", "--yes", action="store_true")
    rm.set_defaults(func=cmd_delete)

    show = sub.add_parser("show")
    show.add_argument("id")
    show.set_defaults(func=cmd_show)

    exp = sub.add_parser("export")
    exp.add_argument("--format", choices=["csv", "json", "text"], default="text")
    exp.add_argument("--output", "-o", default="-")
    exp.set_defaults(func=cmd_export)

    return p


def run_cli() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        logger.error("%s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(run_cli())
