# Trade Log

## Day 0 — EOD Snapshot (pre-launch baseline)

**Portfolio:** $100,000.00 | **Cash:** $100,000.00 (100%) | **Day P&L:** $0 | **Phase P&L:** $0

No positions yet. Bot launches tomorrow. (Paper trading — no real money.)

## Jul 21 — EOD Snapshot (Day 2, Tuesday)

**Portfolio:** $100,000.00 | **Cash:** $100,000.00 (100%) | **Day P&L:** $0.00 (0.00%) | **Phase P&L:** $0.00 (0.00%)

| Ticker/OCC | Shares/Contracts | Entry | Close | Day Chg | Unrealized P&L | Stop/Close Plan |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | No open positions |

**Notes:** Flat day — account sits fully in cash with zero open positions and zero trades executed today or this week. Portfolio value is unchanged from yesterday's $100,000 baseline, so both Day P&L and Phase P&L are flat. No stops to manage since nothing is open. Capital remains available to deploy on the next qualifying setup per the strategy rulebook (max 3 new trades/week, 75-85% target deployment).

## Jul 22 — Market-Open Execution (Day 3, Wednesday)

**Challenge status:** Day 3 of 30. 28 days remaining to 2026-08-19 deadline. Equity $100,000 -> target $150,000. On track (early days, first trades of the challenge).

**Catalyst (from RESEARCH-LOG 2026-07-22 18:19 UTC cycle):** XLE (Energy) is #1 YTD sector (+29.4%) and #1 July sector (+9%), driven by confirmed, ongoing Iran conflict / Strait of Hormuz oil-supply disruption (Brent +3-4.8%, WTI +3% same day). Multi-source-confirmed, non-contradictory signal — first unambiguous TRADE decision since challenge start.

### Trade 1 — XLE long stock
- **Entry:** 506 sh @ $59.21 avg fill (market order), cost basis $29,960.26
- **Sizing:** 30%-of-equity notional cap binds (30% x $100,000 / ~$59.21 ≈ 507 sh) — used 506 sh, notional $29,960 (29.96% of equity)
- **Stop:** 10% trailing stop GTC placed and confirmed, initial stop $53.298 (order id 534e3952-2f2b-4d86-85a7-ed462db26843)
- **Max-loss check (Rule 3):** 506 sh x $5.921 (10% trail distance) = $2,996 = 3.0% of $100,000 equity — well inside 8% cap
- **Thesis:** Energy sector leadership + active oil-supply catalyst; near 52wk high ($42.05-63.46 range) with clean multi-source confirmation
- **Target:** $67 initial reference (+13.1% from entry); trailing stop tightens per Core Rule 6 (7% at +15%, 5% at +20%) rather than a hard cap
- **R:R:** ~2:1 based on $67 target vs. 10% trail stop distance

### Trade 2 — XLE 58.50 call, 2026-08-21 exp (defined-risk sleeve)
- **OCC symbol:** XLE260821C00058500
- **Entry:** 10 contracts @ $2.33 avg fill (market order), cost basis $2,330
- **Strike/Expiration/DTE:** $58.50 strike, 2026-08-21 expiration, 30 DTE (clears >=7 DTE floor)
- **Risk type:** Defined-risk (long call, buy-to-open) — max loss = premium paid = $2,330 = 2.3% of $100,000 equity, well inside 8% cap
- **Thesis:** Same XLE/oil catalyst as Trade 1, smaller leveraged sleeve alongside the core stock position, not a replacement
- **Stop/close plan:** Close at -50% premium (~$1.17/contract, ~$1,165 total) or +50-100% gain; option stops are not natively supported by Alpaca so this is enforced manually via midday/EOD workflows
- **Target:** +50-100% gain per Options Rules
- **R:R:** ~1:1 to 2:1 depending on exit (-50% stop vs. +50-100% target)

**Positions after trade:** 2 of 8 max (1 stock + 1 option). PERPLEXITY_API_KEY and ClickUp creds (CLICKUP_API_KEY/WORKSPACE_ID/CHANNEL_ID) still missing this cycle — no blocker, only affects research-cycle fallback (WebSearch) and notification fallback (local DAILY-SUMMARY.md).
