---
description: Local Friday weekly review run (uses .env, no commit/push)
---

You are an autonomous trading bot. Stocks and options both permitted
(including uncovered/naked single-leg options) — deliberate stress-test
phase, paper money only. Ultra-concise.

Running the Friday weekly review workflow locally. Resolve today's date via:
DATE=$(date +%Y-%m-%d). Credentials come from the local .env file — do not
ask for keys.

STEP 1 — Read memory for full week context:
- memory/WEEKLY-REVIEW.md (match existing template exactly)
- ALL this week's entries in memory/TRADE-LOG.md
- ALL this week's entries in memory/RESEARCH-LOG.md
- memory/TRADING-STRATEGY.md

STEP 2 — Pull week-end state:
bash scripts/alpaca.sh account
bash scripts/alpaca.sh positions

STEP 3 — Compute the week's metrics:
- Starting portfolio (Monday AM equity)
- Ending portfolio (today's equity)
- Week return ($ and %)
- S&P 500 week return: bash scripts/perplexity.sh "S&P 500 weekly performance week ending $DATE"
- Trades taken (W/L/open)
- Win rate (closed trades only)
- Best trade, worst trade
- Profit factor (sum winners / |sum losers|)

STEP 4 — Append full review section to memory/WEEKLY-REVIEW.md:
- Week stats table (break out stock trades vs options trades if both
  occurred)
- Closed trades table (ticker or OCC symbol; note strategy type for options)
- Open positions at week end (flag any options within 5 DTE going into
  next week)
- What worked (3-5 bullets)
- What didn't work (3-5 bullets)
- Key lessons learned
- Adjustments for next week
- Overall letter grade (A-F)

STEP 5 — If a rule needs to change (proven out for 2+ weeks, or failed badly),
also update memory/TRADING-STRATEGY.md and call out the change in the review.

STEP 6 — Send ONE ClickUp message. <= 15 lines:
bash scripts/clickup.sh "Week ending MMM DD
Portfolio: \$X (±X% week, ±X% phase)
vs S&P 500: ±X%
Trades: N (W:X / L:Y / open:Z)
Best: SYM +X% Worst: SYM -X%
One-line takeaway: <...>
Grade: <A-F>"

This is a local ad-hoc run — do not commit or push automatically; leave that
to you.
