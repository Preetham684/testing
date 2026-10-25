#!/usr/bin/env python3
"""PocketPilot ledger. Standard library only. Stores a small JSON file in
$SKILL_DATA_DIR (falls back to ./data) so the estimated balance, spending
history and bills persist between conversations."""
import argparse, json, os, sys
from datetime import date, datetime, timedelta

DIR = os.environ.get("SKILL_DATA_DIR") or os.path.join(os.getcwd(), "data")
PATH = os.path.join(DIR, "ledger.json")


def load():
    if not os.path.exists(PATH):
        return {"balance": None, "balance_date": None, "entries": [], "bills": []}
    with open(PATH) as f:
        return json.load(f)


def save(d):
    os.makedirs(DIR, exist_ok=True)
    with open(PATH, "w") as f:
        json.dump(d, f, indent=1)


def today(a):
    return datetime.strptime(a.today, "%Y-%m-%d").date() if getattr(a, "today", None) else date.today()


def est_balance(d):
    if d["balance"] is None:
        return None
    base = datetime.strptime(d["balance_date"], "%Y-%m-%d").date()
    total = d["balance"]
    for e in d["entries"]:
        if datetime.strptime(e["date"], "%Y-%m-%d").date() >= base:
            total += e["amount"]
    return total


def cmd_set_balance(a):
    d = load()
    d["balance"] = a.amount
    d["balance_date"] = today(a).isoformat()
    save(d)
    print(f"Balance set to ${a.amount:,.2f} as of {d['balance_date']}. Estimates start from here.")


def cmd_add(a):
    """amount: negative = money out, positive = money in. kind: spend|income|bill|other"""
    d = load()
    when = a.date or today(a).isoformat()
    d["entries"].append({"date": when, "amount": a.amount, "kind": a.kind, "note": a.note or ""})
    save(d)
    b = est_balance(d)
    tail = f" Estimated balance: ${b:,.2f}." if b is not None else ""
    print(f"Logged {a.kind} ${a.amount:,.2f} on {when}.{tail}")


def cmd_balance(a):
    d = load()
    b = est_balance(d)
    if b is None:
        print("No balance on file. Ask the student for their current balance.")
        return
    age = (today(a) - datetime.strptime(d["balance_date"], "%Y-%m-%d").date()).days
    note = " Over 30 days since the last confirmed balance, so ask for a fresh one." if age > 30 else ""
    print(f"Estimated balance: ${b:,.2f} (last confirmed {d['balance_date']}, {age} days ago).{note}")


def cmd_bill_add(a):
    d = load()
    d["bills"] = [x for x in d["bills"] if x["name"].lower() != a.name.lower()]
    d["bills"].append({"name": a.name, "amount": a.amount, "due": a.due, "paid": False})
    save(d)
    print(f"Saved bill: {a.name} ${a.amount:,.2f} due {a.due}.")


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
    items = []
    for x in d["bills"]:
        if x["paid"]:
            continue
        due = datetime.strptime(x["due"], "%Y-%m-%d").date()
        if due <= end:
            items.append((due, x))
    items.sort(key=lambda z: z[0])
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
    spend = [e for e in d["entries"] if e["kind"] == "spend"
             and start < datetime.strptime(e["date"], "%Y-%m-%d").date() <= t]
    days_seen = len({e["date"] for e in spend})
    if days_seen < 3:
        print("Not enough spending logged yet to see a pace (need about 3 days of data).")
        return
    total = -sum(e["amount"] for e in spend)
    avg = total / a.days
    msg = f"Spending pace: ${avg:,.2f}/day over the last {a.days} days (${total:,.2f} total)."
    if a.target is not None:
        msg += f" Target: ${a.target:,.2f}/day. " + ("Over target." if avg > a.target else "Under target.")
    print(msg)
    print(f"AVG={avg:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", help="YYYY-MM-DD, for testing only")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("set-balance"); s.add_argument("--amount", type=float, required=True); s.set_defaults(fn=cmd_set_balance)
    s = sub.add_parser("add")
    s.add_argument("--amount", type=float, required=True)
    s.add_argument("--kind", choices=["spend", "income", "bill", "other"], required=True)
    s.add_argument("--note"); s.add_argument("--date"); s.set_defaults(fn=cmd_add)
    s = sub.add_parser("balance"); s.set_defaults(fn=cmd_balance)
    s = sub.add_parser("bill-add")
    s.add_argument("--name", required=True); s.add_argument("--amount", type=float, required=True)
    s.add_argument("--due", required=True); s.set_defaults(fn=cmd_bill_add)
    s = sub.add_parser("bill-paid"); s.add_argument("--name", required=True); s.set_defaults(fn=cmd_bill_paid)
    s = sub.add_parser("bills-due"); s.add_argument("--within", type=int, default=7); s.set_defaults(fn=cmd_bills_due)
    s = sub.add_parser("pace")
    s.add_argument("--days", type=int, default=7); s.add_argument("--target", type=float); s.set_defaults(fn=cmd_pace)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
