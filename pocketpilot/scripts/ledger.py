#!/usr/bin/env python3
"""PocketPilot ledger. Standard library only.

Storage: one JSON file, kept in the student's private sandbox. The path is
$SKILL_DATA_DIR if set, otherwise $HOME/.pocketpilot (HOME persists per
student). It never uses the Skill folder, which is replaced on every start.
The file is NOT encrypted: it is created readable by its owner only (0600),
holds amounts, dates and short notes, and must never hold account numbers.
"""
import argparse, json, os, sys, tempfile
from datetime import date, datetime, timedelta


def data_dir():
    d = os.environ.get("SKILL_DATA_DIR")
    if d:
        return d
    home = os.environ.get("HOME")
    if home:
        return os.path.join(home, ".pocketpilot")
    sys.exit("ERROR: no storage location. Neither SKILL_DATA_DIR nor HOME is set, "
             "so nothing was saved. Tell the student their data could not be stored.")


def path():
    return os.path.join(data_dir(), "ledger.json")


def blank():
    return {"v": 2, "balance": None, "balance_date": None, "balance_seq": 0,
            "entries": [], "bills": []}


def load():
    p = path()
    if not os.path.exists(p):
        return blank()
    try:
        with open(p) as f:
            d = json.load(f)
    except (ValueError, OSError):
        sys.exit(f"ERROR: the ledger file at {p} is unreadable. Do not overwrite it; "
                 "ask the student whether to restore or start fresh (wipe --confirm).")
    d.setdefault("balance_seq", 0)
    return d


def save(d):
    dd = data_dir()
    os.makedirs(dd, mode=0o700, exist_ok=True)
    try:
        os.chmod(dd, 0o700)
    except OSError:
        pass
    fd, tmp = tempfile.mkstemp(dir=dd)           # atomic write: never a half-written file
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(d, f, indent=1)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path())
    except OSError as e:
        sys.exit(f"ERROR: could not save ({e}). Tell the student nothing was saved.")


def parse(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        sys.exit(f"ERROR: dates must look like 2026-10-24, got '{s}'.")


def today(a):
    return parse(a.today) if getattr(a, "today", None) else date.today()


def est_balance(d):
    """Confirmed balance + entries logged AFTER it was confirmed and dated on/after it.
    Entries logged before a confirmation are already inside that balance."""
    if d["balance"] is None:
        return None
    base = parse(d["balance_date"])
    total = d["balance"]
    for i, e in enumerate(d["entries"]):
        if i >= d["balance_seq"] and parse(e["date"]) >= base:
            total += e["amount"]
    return total


def cmd_set_balance(a):
    d = load()
    d["balance"] = a.amount
    d["balance_date"] = today(a).isoformat()
    d["balance_seq"] = len(d["entries"])        # everything logged so far is now inside this balance
    save(d)
    print(f"Balance confirmed at ${a.amount:,.2f} on {d['balance_date']}. "
          "Earlier logged items are not counted again.")


def cmd_add(a):
    d = load()
    amt = abs(a.amount)
    amt = -amt if a.kind in ("spend", "bill") else amt if a.kind == "income" else a.amount
    when = a.date or today(a).isoformat()
    parse(when)
    note = (a.note or "").strip()

    if a.ref:
        for e in d["entries"]:
            if e.get("ref") == a.ref:
                print(f"DUPLICATE: reference {a.ref} was already logged ({e['kind']} ${e['amount']:,.2f} on {e['date']}). Not logged again.")
                return
    if not a.force:
        for e in d["entries"]:
            close = abs((parse(e["date"]) - parse(when)).days) <= 1
            if close and e["kind"] == a.kind and abs(e["amount"] - amt) < 0.005:
                print(f"POSSIBLE DUPLICATE of '{e.get('note','')}' (${e['amount']:,.2f} on {e['date']}). "
                      "NOT logged. Ask the student if it is a separate purchase; if yes, run again with --force.")
                return

    d["entries"].append({"date": when, "amount": amt, "kind": a.kind, "note": note, "ref": a.ref or ""})
    save(d)
    b = est_balance(d)
    tail = f" Estimated balance: ${b:,.2f}." if b is not None else ""
    print(f"Logged {a.kind} ${amt:,.2f} on {when}.{tail}")


def cmd_balance(a):
    d = load()
    b = est_balance(d)
    if b is None:
        print("No balance on file. Ask the student for their current balance.")
        return
    age = (today(a) - parse(d["balance_date"])).days
    note = " More than 30 days since the last confirmed balance, so ask for a fresh one." if age > 30 else ""
    print(f"Estimated balance: ${b:,.2f} (last confirmed {d['balance_date']}, {age} days ago).{note}")


def cmd_bill_add(a):
    d = load()
    parse(a.due)
    d["bills"] = [x for x in d["bills"] if x["name"].lower() != a.name.lower()]
    d["bills"].append({"name": a.name, "amount": abs(a.amount), "due": a.due, "paid": False})
    save(d)
    print(f"Saved bill: {a.name} ${abs(a.amount):,.2f} due {a.due}.")


def cmd_bill_paid(a):
    d = load()
    hit = [x for x in d["bills"] if x["name"].lower() == a.name.lower()]
    if not hit:
        print(f"No bill named {a.name}.")
        return
    hit[0]["paid"] = True
    save(d)
    print(f"Marked {a.name} paid.")


def cmd_bills_due(a):
    d = load()
    t = today(a)
    end = t + timedelta(days=a.within)
    items = sorted(((parse(x["due"]), x) for x in d["bills"] if not x["paid"] and parse(x["due"]) <= end),
                   key=lambda z: z[0])
    if not items:
        print(f"Nothing due in the next {a.within} days.")
        return
    total = 0.0
    for due, x in items:
        gap = (due - t).days
        when = "OVERDUE" if gap < 0 else "today" if gap == 0 else f"in {gap} day{'s' if gap != 1 else ''}"
        print(f"{x['name']}: ${x['amount']:,.2f} due {x['due']} ({when})")
        total += x["amount"]
    print(f"Total due within {a.within} days: ${total:,.2f}")


def cmd_pace(a):
    d = load()
    t = today(a)
    start = t - timedelta(days=a.days)
    spend = [e for e in d["entries"] if e["kind"] == "spend" and start < parse(e["date"]) <= t]
    if len({e["date"] for e in spend}) < 3:
        print("Not enough spending logged yet to see a pace (need about 3 days of data).")
        return
    total = -sum(e["amount"] for e in spend)
    avg = total / a.days
    msg = f"Spending pace: ${avg:,.2f}/day over the last {a.days} days (${total:,.2f} total)."
    if a.target is not None:
        msg += f" Target: ${a.target:,.2f}/day. " + ("Over target." if avg > a.target else "Under target.")
    print(msg)
    print(f"AVG={avg:.2f}")


def cmd_status(a):
    p = path()
    inside = os.path.abspath(p).startswith(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    print(f"Data file: {p}")
    print("Exists: " + ("yes" if os.path.exists(p) else "no"))
    if os.path.exists(p):
        print(f"Permissions: {oct(os.stat(p).st_mode & 0o777)}")
    if inside:
        print("WARNING: data is inside the Skill folder and will be lost on restart.")


def cmd_wipe(a):
    if not a.confirm:
        print("Not wiped. Run again with --confirm only after the student clearly says to erase their PocketPilot data.")
        return
    if os.path.exists(path()):
        os.remove(path())
    print("PocketPilot data erased.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", help="YYYY-MM-DD, for testing only")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set-balance"); s.add_argument("--amount", type=float, required=True); s.set_defaults(fn=cmd_set_balance)
    s = sub.add_parser("add")
    s.add_argument("--amount", type=float, required=True)
    s.add_argument("--kind", choices=["spend", "income", "bill", "other"], required=True)
    s.add_argument("--note"); s.add_argument("--date")
    s.add_argument("--ref", help="unique id of the source, e.g. the email message id")
    s.add_argument("--force", action="store_true", help="log even if it looks like a duplicate")
    s.set_defaults(fn=cmd_add)
    s = sub.add_parser("balance"); s.set_defaults(fn=cmd_balance)
    s = sub.add_parser("bill-add")
    s.add_argument("--name", required=True); s.add_argument("--amount", type=float, required=True)
    s.add_argument("--due", required=True); s.set_defaults(fn=cmd_bill_add)
    s = sub.add_parser("bill-paid"); s.add_argument("--name", required=True); s.set_defaults(fn=cmd_bill_paid)
    s = sub.add_parser("bills-due"); s.add_argument("--within", type=int, default=7); s.set_defaults(fn=cmd_bills_due)
    s = sub.add_parser("pace")
    s.add_argument("--days", type=int, default=7); s.add_argument("--target", type=float); s.set_defaults(fn=cmd_pace)
    s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("wipe"); s.add_argument("--confirm", action="store_true"); s.set_defaults(fn=cmd_wipe)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
