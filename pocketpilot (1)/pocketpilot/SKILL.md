---
name: pocketpilot
description: Shows a student what a purchase costs them today and what it costs their savings-goal date, and gives a daily safe-to-spend number. Use when the student asks if they can afford something, whether to buy something, how much they can spend today, how to stretch a financial-aid refund, how far along a savings goal is, a financial plan for a trip or big expense, or reminders for bills and money due.
---

# PocketPilot

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

**Morning money briefing (email watch + reminders).**
Setup (once):
- Ask which Google accounts to watch (personal and school); ask Cubbie to connect any that are not linked yet.
- Ask what time they want their morning briefing, suggest 7:30 am, and create a daily scheduled check-in. Let them change or stop it. Offer an optional evening check.

Each morning:
1. Search the synced email of every connected account for money-related emails since the last check: bank and credit card alerts, statement-ready and payment-due notices, rent and utilities, tuition, fee and financial-aid messages, subscription renewals, receipts, and requests to pay someone. Include emails the student sent themselves (notes to self, forwarded bills, messages about paying a friend) if they show up in search. Ignore anything not about money.
2. Skip anything already counted (remember it by sender, date and amount).
3. List each new item with amount, due date and source account, and ask yes or no before counting it. Save confirmed bills as "due" items with a date and amount. When the student says they paid something, mark it paid.
4. Text one short briefing: what is due today and in the next 7 days (credit card, rent, anyone they owe, subscriptions), any new money email, safe to spend today (run the daily script), and one action to stay on track. If a bill would leave them short, say by how much and what covering it from savings does to the goal date.
5. If nothing is due within 7 days and nothing is new, send no text.

Limits to say honestly:
- Statement-ready emails usually contain no numbers. Say you cannot see inside the statement and ask the student to text the balance or send a screenshot or PDF.
- Checks run at the chosen times, not the instant an email arrives.
- Never ask for a bank login. Do not remember full account numbers; refer to accounts by name only.

**Financial plan for a trip or big expense.** Use when the student asks for help planning for something like a December trip to Hawaii.
1. Ask only for what is missing: destination, month, travelers, and what they have saved.
2. Search the web for current typical costs (flights, lodging, food, activities) and show them as estimates with a range.
3. Run `python3 scripts/calc.py trip --cost C --saved S --months N --monthly M` to get the monthly and weekly amount needed and how it compares with what they save now.
4. Write the plan as a Google Doc with: goal and date, cost breakdown with ranges, monthly and weekly savings target, what to cut or delay, a month-by-month checklist, and a list of assumptions.
5. Tell the student the plan is ready and give the link. Create it in their Google Drive only after they say yes, and do not share it with anyone.
If Google is not connected, ask them to connect it, or put the plan in a document file instead.

**Cooling-off.** If the student is tempted by something, offer to check in 48 hours later with "Still want it?"

**Investing.** Only after about 30 days of cushion, no high-interest debt, and a starter fund. For goals under about three years suggest savings or CDs, not stocks. Use Cubbie's normal investing help, with no picks.

## When things go wrong
- Email not connected: say so, ask them to connect Google, or accept numbers by text.
- Missing number: ask for just that one thing.
- Script error or odd result: say you couldn't calculate it and ask the student to recheck the inputs.
