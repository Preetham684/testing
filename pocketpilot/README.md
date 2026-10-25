# PocketPilot

**Spend like yourself. Plan like your future self.**

A Cubbie Skill for the Cubbie Hackathon (Track 1). PocketPilot gives students the one number that matters: *how much can I spend today without hurting tomorrow?*

- Daily safe-to-spend number, in a morning text
- "Should I buy this?": cash today and goal date, side by side
- Refund runway, goal check, and trip plans saved as a Google Doc
- Updates from bank alert emails. No bank login, no moving money.

## Example

> **You:** Bro, I want this concert ticket. It's $300.
> **Cubbie:** BUY NOW: negative cash, goal date slips about 5 weeks. WAIT: revisit when cash flow is healthier. GO CHEAPER: a $100 alternative keeps more toward your goal. My vote? Wait 48 hours.

## Install

Text this folder's GitHub link to Cubbie.

## Under the hood

`scripts/calc.py` (spending math) and `scripts/ledger.py` (running balance, bills, spending pace). Standard library only, so no `cubbie.yaml` is needed.

This is budgeting math and education, not professional financial advice.
