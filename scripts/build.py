"""Build the salary-history page from template.html + data/employees.json.

Usage:  python scripts/build.py [output.html]
Default output: out/vyvoj-mezd.html (git-ignored). Exits 1 on invalid data.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KINDS = {None, "pay", "info", "leave", "dpp", "end"}


def validate(data):
    errors = []
    names = set()
    for i, p in enumerate(data):
        who = p.get("name") or f"#{i}"
        if not p.get("name"):
            errors.append(f"{who}: missing name")
        if who in names:
            errors.append(f"{who}: duplicate name")
        names.add(who)
        if not DATE.match(str(p.get("start", ""))):
            errors.append(f"{who}: bad start {p.get('start')!r}")
        if p.get("end") is not None and not DATE.match(str(p["end"])):
            errors.append(f"{who}: bad end {p['end']!r}")
        if not isinstance(p.get("events"), list) or not p["events"]:
            errors.append(f"{who}: events must be a non-empty list")
            continue
        if not isinstance(p.get("issues", []), list):
            errors.append(f"{who}: issues must be a list")
        for e in p["events"]:
            if not DATE.match(str(e.get("from", ""))):
                errors.append(f"{who}: event with bad date {e.get('from')!r}")
            if e.get("salary") is not None and not isinstance(e["salary"], (int, float)):
                errors.append(f"{who} {e.get('from')}: salary must be a number or null")
            if e.get("kind") not in KINDS:
                errors.append(f"{who} {e.get('from')}: unknown kind {e.get('kind')!r}")
            if not e.get("doc"):
                errors.append(f"{who} {e.get('from')}: missing doc")
    return errors


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "out" / "vyvoj-mezd.html"
    data = json.loads((ROOT / "data" / "employees.json").read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print("INVALID DATA:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)
    for p in data:
        p["events"].sort(key=lambda e: e["from"])
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    if tpl.count("/*DATA*/[]") != 1:
        print("template.html must contain exactly one /*DATA*/[] marker", file=sys.stderr)
        sys.exit(1)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl.replace("/*DATA*/[]", payload), encoding="utf-8")
    print(f"employees: {len(data)}; events: {sum(len(p['events']) for p in data)}; written: {out}")


if __name__ == "__main__":
    main()
