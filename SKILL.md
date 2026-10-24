---
name: runway-future-fund
description: Shows a student what a purchase costs them today and what it costs their savings-goal date, and gives a daily safe-to-spend number. Use when the student asks if they can afford something, whether to buy something, how much they can spend today, how to stretch a financial-aid refund, or how far along a savings goal is.
---

# Runway + Future Fund

Two questions, one text thread: "Can I afford this today?" and "What does it cost my goal?"

## Rules
- All math comes from `scripts/calc.py`. Never calculate in your head.
- Show and suggest only. Never move money, pay, or cancel anything. No bank logins.
- Education, not advice: no stock picks, no promised returns. Call projections illustrations (no interest assumed).
- Texts are short, one idea each, no jargon. Put anything long in a document.
- Show every charge found in email or a receipt photo and get a yes before counting it.

## Setup (once, one question at a time, skip anything already remembered)
Ask for: checking balance, next payday and days until it, bills due before then, goal (amount and deadline), amount saved, monthly contribution. Remember them. Treat the monthly contribution as a bill.
Update the balance when the student texts a short log like "coffee 6".

## Flows

**Goal check.** Run `python3 scripts/calc.py goal --saved S --monthly M --months N --target T`. Reply with the projection, the shortfall, and the monthly amount needed.

**Should I buy this?** Run `python3 scripts/calc.py buy --price P --monthly M --balance B --bills X --buffer F --days D`. Give two lines: today's cash and goal date.

**Compare three ways.** Run `python3 scripts/calc.py compare --price P --alt A --monthly M --balance B --bills X --buffer F --days D`. Show buy now, wait two months, and the cheaper alternative side by side.

**Daily number.** Run `python3 scripts/calc.py daily --balance B --bills X --buffer F --days D`. Offer a daily check-in and let the student choose the time. End with one line on goal status.

**Refund stretch.** Same formula, with the refund as the balance and days until the next paycheck. Offer a goal slider: more toward the goal lowers the daily number.

**Heads-ups.** Search the student's email for upcoming bills and charges, list what you found, and ask which to count. If a bill would leave them short, say by how much and what covering it from savings does to the goal date.

**Cooling-off.** If the student is tempted by something, offer to check in 48 hours later with "Still want it?"

**Investing.** Only after about 30 days of cushion, no high-interest debt, and a starter fund. For goals under about three years suggest savings or CDs, not stocks. Use Cubbie's normal investing help, with no picks.

## When things go wrong
- Email not connected: say so, ask them to connect Google, or accept numbers by text.
- Missing number: ask for just that one thing.
- Script error or odd result: say you couldn't calculate it and ask the student to recheck the inputs.
