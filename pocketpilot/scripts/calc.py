#!/usr/bin/env python3
"""Runway + Future Fund math. Standard library only. Daily numbers round down."""
import argparse, math


def pool(a):
    return a.balance - a.bills - a.buffer


def per_day(p, days):
    return math.floor(p / days)


def cmd_daily(a):
    p = pool(a)
    if p < 0:
        print(f"Short by ${-p:,.2f} before next income. Safe to spend today: $0.")
    else:
        print(f"Safe to spend today: ${per_day(p, a.days)}/day (${p:,.2f} over {a.days} days).")


def cmd_goal(a):
    projected = a.saved + a.monthly * a.months
    gap = a.target - projected
    if gap <= 0:
        print(f"At ${a.monthly:,.0f}/month you'll reach ${projected:,.0f}, past your ${a.target:,.0f} goal.")
        return
    needed = math.ceil((a.target - a.saved) / a.months)
    line = (f"At ${a.monthly:,.0f}/month you'll reach ${projected:,.0f}, "
            f"${gap:,.0f} short of ${a.target:,.0f}. Save ${needed:,}/month to hit it.")
    if a.monthly > 0:
        line += f" Or keep ${a.monthly:,.0f} and reach it in {math.ceil((a.target - a.saved) / a.monthly)} months."
    print(line)


def cmd_trip(a):
    need = a.cost - a.saved
    if need <= 0:
        print(f"You already have the ${a.cost:,.0f}. Nothing more to save.")
        return
    monthly_needed = math.ceil(need / a.months)
    weekly_needed = math.ceil(need / (a.months * 4.345))
    line = (f"To have ${a.cost:,.0f} in {a.months} months with ${a.saved:,.0f} saved, "
            f"save ${monthly_needed:,}/month (about ${weekly_needed:,}/week).")
    if a.monthly >= 0:
        projected = a.saved + a.monthly * a.months
        if projected >= a.cost:
            line += f" Your current ${a.monthly:,.0f}/month already covers it."
        else:
            line += f" At your current ${a.monthly:,.0f}/month you'd have ${projected:,.0f}, ${a.cost - projected:,.0f} short."
    print(line)


def cmd_shortfall(a):
    p = pool(a)
    target = per_day(p, a.days) if p > 0 else 0
    projected = a.avg * a.days
    if a.avg <= target:
        print(f"On pace: ${a.avg:,.0f}/day vs a ${target}/day target.")
        return
    short = projected - p
    last = int(p // a.avg) if a.avg > 0 else a.days
    print(f"Pace ${a.avg:,.0f}/day vs target ${target}/day. At this pace you'd be ${short:,.0f} short by payday, "
          f"running out around day {last} of {a.days}. To fix it, spend about ${target}/day "
          f"(${a.avg - target:,.0f}/day less).")


def delay_text(price, monthly):
    if monthly <= 0:
        return "an unknown amount (no monthly savings set)"
    days = round(price / monthly * 30.44)
    if days < 21:
        return f"about {days} days"
    return f"about {round(days / 7)} weeks"


def cash_text(p, x, days):
    if p - x < 0:
        return "negative, can't come from checking"
    return f"${per_day(p - x, days)}/day"


def cmd_buy(a):
    p = pool(a)
    before = per_day(p, a.days) if p >= 0 else 0
    if p - a.price < 0:
        cash = "goes negative, can't come from checking"
    else:
        cash = f"drops from ${before} to ${per_day(p - a.price, a.days)}/day"
    print(f"Today: daily number {cash}.")
    print(f"Goal: pushes your date back {delay_text(a.price, a.monthly)}.")


def cmd_compare(a):
    p = pool(a)
    before = per_day(p, a.days) if p >= 0 else 0
    print(f"Buy now (${a.price:,.0f}): {cash_text(p, a.price, a.days)}; goal {delay_text(a.price, a.monthly)} later")
    print(f"Wait 2 months: unchanged at ${before}/day; goal {delay_text(a.price, a.monthly)} later if you still buy")
    print(f"Alternative (${a.alt:,.0f}): {cash_text(p, a.alt, a.days)}; goal {delay_text(a.alt, a.monthly)} later")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, **args):
        s = sub.add_parser(name)
        for k, t in args.items():
            s.add_argument(f"--{k}", type=t, required=True)
        s.set_defaults(fn=fn)

    base = dict(balance=float, bills=float, buffer=float, days=int)
    add("daily", cmd_daily, **base)
    add("goal", cmd_goal, saved=float, monthly=float, months=int, target=float)
    add("buy", cmd_buy, price=float, monthly=float, **base)
    add("compare", cmd_compare, price=float, alt=float, monthly=float, **base)
    add("shortfall", cmd_shortfall, avg=float, **base)
    add("trip", cmd_trip, cost=float, saved=float, months=int, monthly=float)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
