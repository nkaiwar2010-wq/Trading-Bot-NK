---
description: Read-only snapshot of account, positions, open orders, and stops
---

Print a clean ad-hoc snapshot. No state changes, no orders, no file writes.

1. bash scripts/alpaca.sh account
2. bash scripts/alpaca.sh positions
3. bash scripts/alpaca.sh orders

Format the output as a single concise summary:

Portfolio — Equity: $X | Cash: $X (X%) | Buying power: $X
Daytrade count: N/4 | PDT: <ok/at-risk>

Positions:
SYM/OCC | Sh/Contracts | Entry -> Now | Unrealized P&L | Stop/Close Plan
(for options, pull strike/expiration/DTE from the position's OCC symbol)

Open orders:
TYPE | SYM/OCC | qty | trail/stop/limit | order_id

No commentary unless something is broken (a stock position without a
trailing stop, a stop below current price, or an options position within
2 DTE with no logged close plan).
