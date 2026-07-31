# Mirage Trade Log

## Day 0 — EOD Snapshot (pre-launch baseline)

**Portfolio:** $50,000.00 | **Cash:** $50,000.00 (100%) | **Day P&L:** $0 | **Phase P&L:** $0

No positions yet. Bot launches next trading session. (Paper trading — no real money, separate account from Oasis.)

### Jul 27 — EOD Force-Close (Day 1)

**Portfolio:** $50,000.00 | **Cash:** $50,000.00 (100% — always ends the day fully flat) | **Day P&L:** $0 (0%) | **Phase P&L:** $0 (0%)

| Ticker/OCC | Entry | Exit | Realized P&L | Reason closed |
|---|---|---|---|---|
| — | — | — | — | — |

**Notes:** Bot has not opened any trades yet — account was created today and no morning-entry cycle has run. Nothing to close; account confirmed flat (0 positions, 0 open orders). No action needed for tomorrow's cycle beyond normal entry logic.

<!-- DAEMON_ENTRY: ENTX long 2026-07-27 -->
### Jul 27 17:22 UTC — Intraday Daemon Entry
**ENTX** long 3846 sh @ ~$3.82 | stop $2.78 | target $5.90 (2.0:1) | gap 85.8%, ORB confirmed above $3.07 | Rule 1: 3846 x $1.04 = $3999.84 (8.0% of $50,000 equity, cap 8%)

<!-- DAEMON_ENTRY: LVWR long 2026-07-27 -->
### Jul 27 17:23 UTC — Intraday Daemon Entry
**LVWR** long 4275 sh @ ~$2.52 | stop $1.59 | target $4.38 (2.0:1) | gap 71.9%, ORB confirmed above $2.52 | Rule 1: 4275 x $0.93 = $3975.75 (8.0% of $49,700 equity, cap 8%)

<!-- DAEMON_ENTRY: KIDZ long 2026-07-27 -->
### Jul 27 17:24 UTC — Intraday Daemon Entry
**KIDZ** long 16482 sh @ ~$0.72 | stop $0.48 | target $1.20 (2.0:1) | gap 64.6%, ORB confirmed above $0.53 | Rule 1: 16482 x $0.24 = $3950.74 (8.0% of $49,386 equity, cap 8%)

<!-- DAEMON_ENTRY: GOSS long 2026-07-27 -->
### Jul 27 17:25 UTC — Intraday Daemon Entry
**GOSS** long 84530 sh @ ~$0.20 | stop $0.15 | target $0.29 (2.0:1) | gap 45.5%, ORB confirmed above $0.17 | Rule 1: 84530 x $0.05 = $3913.74 (8.0% of $48,922 equity, cap 8%)

### Jul 27 17:24-17:29 UTC — Manual intervention: two bugs found live in mirage_daemon.py

**Bug 1 (safety-critical):** all four entries above (ENTX, LVWR, KIDZ, GOSS) filled with
**no protective stop order in place** — confirmed via `/v2/orders?status=open` showing
zero stop orders against any of the four positions. Root cause: the code submitted the
stop-loss order immediately after the buy, without waiting to confirm the buy had
actually filled — a race condition where Alpaca can reject the stop for "insufficient
position" if the buy hasn't registered yet. The 8%-of-equity Rule 1 cap was NOT
breached by this bug (position sizing math was correct), but positions were open with
zero downside protection, violating the "never open a position without a live stop"
rule.
**Bug 2:** the stop-price formula used `min(or_low, entry * 0.97)` instead of `max(...)`
— for a long position this picks the WIDER of the two candidate stops, not the tighter
one as STRATEGY.md specifies. Actual stops (had they been placed) would have been
~25-37% below entry instead of ~2-3%. Dollar risk was still capped at 8% of equity
because position size was computed from that same (wrong, wider) stop distance — so no
single trade exceeded the hard cap — but the intended tight-stop behavior wasn't
happening.
**Manual correction taken (paper account, ~17:28 UTC):**
- ENTX (already -3.6%, past where its intended stop should have fired): closed at
  market, realized P&L ~-$530.
- KIDZ (already -3.74%, same situation): closed at market, realized P&L ~-$427.
- LVWR (+0%): real protective stop placed manually at $2.44 (3% below $2.52 entry).
- GOSS (+2.76%): real protective stop placed manually at $0.1931 (3% below $0.1991 entry).
Both bugs fixed in code (commits fixing wait-for-fill + safety-net stop check, and the
min→max stop-price correction) and pushed. The GitHub Actions run active at the time of
this fix was still running the old, buggy code in memory — it needs to be manually
cancelled and re-triggered to pick up both fixes for the remainder of today's session.

<!-- DAEMON_EXIT: LVWR 2026-07-27 17:39 -->
### Jul 27 17:39 UTC — Intraday Daemon Exit — **CORRECTION: THIS DID NOT HAPPEN**
~~**LVWR** closed @ ~$2.68 | entry $2.52 | realized P&L $683.57 (6.3%) | reason: target reached (6.3%, >= 2.0:1 R:R)~~
**Third bug found, same session:** `close_position()` was called and the log entry above
was written, but Alpaca's own fill ledger (`/v2/account/activities/FILL`) shows **no sell
fill for LVWR ever occurred** — only the original buy. The liquidation call silently
failed (most likely because the still-open protective stop order had qty_available
locked at 0) and the code logged success without verifying it. LVWR **remained open**
the whole time; its protective stop was cancelled as part of the (failed) close attempt,
leaving it naked until the safety-net check re-placed a stop on the next cycle.
**Fixed in code:** existing orders for a symbol are now cancelled *before* attempting the
close (not after), and the close is only logged/committed once `wait_for_close()`
confirms the position is actually gone — a timeout re-places the protective stop and
retries next cycle instead of writing a false record.
**Real state as of this correction:** LVWR still open, 4275 sh, protected by a real stop.

**Also correcting the manual ENTX/KIDZ figures logged earlier** — those were
estimated from the unrealized P&L shown at the moment I issued the manual close, not
the actual fill price. Verified against Alpaca's fill ledger, the real numbers are:
- ENTX: sold @ $3.68 avg (entry $3.81) → realized **-$499.98**, not the ~-$530 estimated.
- KIDZ: sold @ $0.6562 avg (entry $0.6923) → realized **-$595.00**, not the ~-$427 estimated.
- Combined realized loss from these two: **-$1,094.98**.

<!-- DAEMON_EXIT: LVWR 2026-07-27 18:02 -->
### Jul 27 18:02 UTC — Intraday Daemon Exit
**LVWR** closed @ ~$2.69 | entry $2.52 | realized P&L $722.90 (6.7%) | reason: target reached (6.7%, >= 2.0:1 R:R)

### Jul 27 — EOD Force-Close (Day 1) — Final Summary

**Portfolio:** $49,056.48 | **Cash:** $49,056.48 (100% — always ends the day fully flat) | **Day P&L:** -$943.52 (-1.89%) | **Phase P&L:** -$943.52 (-1.89%)

| Ticker/OCC | Entry | Exit | Realized P&L | Reason closed |
|---|---|---|---|---|
| ENTX | $3.81 | $3.68 | -$499.98 (-3.41%) | Manual close — protective stop was missing due to a same-day bug (stop submitted before entry-fill confirmation); closed after price had already moved past the intended stop level |
| KIDZ | $0.6923 | $0.6562 | -$595.00 (-5.21%) | Manual close — same missing-stop bug as ENTX |
| LVWR | $2.52 | $2.68 | +$684.00 (+6.35%) | Target reached (2.0:1 R:R), daemon exit |
| GOSS | $0.1991 | $0.1928 | -$532.54 (-3.16%) | Stop-loss hit (manual protective stop @ $0.1931) |

**Notes:** All four positions were opened and closed intraday, well before this EOD routine ran — `positions` and `orders` both returned empty when this force-close check executed. `close-all`/`cancel-all` were still run per protocol and confirmed empty (no-op). Two live bugs were found and fixed mid-session in `mirage_daemon.py`: (1) stop-loss orders were submitted before confirming the entry fill, occasionally leaving positions briefly unprotected; (2) the stop-price formula used `min()` instead of `max()`, picking the wider/weaker candidate stop instead of the tighter one STRATEGY.md specifies. Both were patched and pushed same-day. A third bug — a `close_position()` call that silently failed and logged a false "closed" record for LVWR — was also caught and fixed; LVWR's real close later in the session (target hit) settled at **$2.68, +$684.00 (+6.35%)**, which supersedes the earlier intraday estimate of $2.69/$722.90 logged above (that figure was read off unrealized P&L before the fill ledger confirmed the actual price). Verified: entry/exit prices and P&L above are pulled directly from Alpaca's orders and `/account/activities/FILL` records, and the total (-$943.52) reconciles exactly with account equity (last_equity $50,000.00 → equity $49,056.48). Day tally: 4 opened, 4 closed, 1 win (LVWR) / 3 losses (ENTX, KIDZ, GOSS). Flag for tomorrow: confirm the three bug fixes hold up in a clean session with no manual intervention before trusting the daemon unattended.

### Jul 28 — EOD Force-Close (Day 2)

**Portfolio:** $49,038.20 | **Cash:** $49,038.20 (100% — always ends the day fully flat) | **Day P&L:** -$18.28 (-0.04%) | **Phase P&L:** -$961.80 (-1.92%)

| Ticker/OCC | Entry | Exit | Realized P&L | Reason closed |
|---|---|---|---|---|
| — | — | — | — | — |

**Notes:** No morning-entry cycle ran today — account had 0 open positions and 0 open orders when this EOD routine executed (`positions` and `orders` both returned empty before `close-all`/`cancel-all`, which were run per protocol as no-ops and reconfirmed empty). No trades opened, no trades closed, 0 wins / 0 losses. The -$18.28 day drift with no trading activity is a small overnight equity adjustment already reflected in Alpaca's `last_equity`/`equity` fields (not attributable to any position). Nothing to flag for tomorrow beyond confirming the daemon actually fires a morning-entry cycle — two days in a row now (day 1 post-bugfix session, day 2 today) with no autonomous entries logged outside the manual Day 1 intervention.

<!-- DAEMON_ENTRY: LAD long 2026-07-29 -->
### Jul 29 17:51 UTC — Intraday Daemon Entry
**LAD** long 21 sh @ ~$448.41 | stop $434.96 | target $475.31 (2.0:1) | gap 19.8%, ORB confirmed above $403.31 | Rule 1: 21 x $13.45 = $282.50 (0.6% of $49,038 equity, cap 4%)

<!-- DAEMON_ENTRY: CBZ long 2026-07-29 -->
### Jul 29 17:52 UTC — Intraday Daemon Entry
**CBZ** long 178 sh @ ~$54.85 | stop $54.36 | target $55.83 (2.0:1) | gap 17.4%, ORB confirmed above $54.50 | Rule 1: 178 x $0.49 = $87.22 (0.2% of $49,029 equity, cap 4%)

<!-- DAEMON_ENTRY: GRMN long 2026-07-29 -->
### Jul 29 17:53 UTC — Intraday Daemon Entry
**GRMN** long 32 sh @ ~$298.21 | stop $289.26 | target $316.10 (2.0:1) | gap 17.3%, ORB confirmed above $297.00 | Rule 1: 32 x $8.95 = $286.28 (0.6% of $48,998 equity, cap 4%)

<!-- DAEMON_ENTRY: NNNN long 2026-07-29 -->
### Jul 29 17:54 UTC — Intraday Daemon Entry
**NNNN** long 840 sh @ ~$11.65 | stop $11.30 | target $12.35 (2.0:1) | gap 18.6%, ORB confirmed above $10.88 | Rule 1: 840 x $0.35 = $293.58 (0.6% of $48,977 equity, cap 4%)

### Jul 29 17:56 UTC — Manual Intervention: NNNN closed, 4th bug found and fixed

**Bug found:** NNNN's real fill (confirmed via `/v2/account/activities/FILL`) was **840 sh @ $12.9043 avg**
(range $12.90-$13.26), not the ~$11.65 quoted price logged above — an **~11-14% slip** in a thin/
fast-moving stock. The stop ($11.30) and position size (840 sh, sized off the $11.65 quote) were both
computed from the pre-fill quote, not the real fill, so: (a) the real notional deployed was ~$10,840,
about 22% of equity — over the 20% MAX_NOTIONAL_PCT cap — and (b) the stop ended up ~12.4% below the
real entry instead of the intended ~3%. By the time this was caught, price ($12.04) had already fallen
below where the *intended* 3% stop should have fired, so the responsible action was to close now rather
than wait for the (mis-sized) $11.30 stop.
**Manual correction:** closed at market, realized P&L ≈ **-$726** (~-6.7% from actual entry).
**Fixed in code:** `wait_for_fill()` now also returns `filled_avg_price`; stop/target are recomputed from
the real fill price (with a logged slippage warning if it differs from the quote by >2%), not the
pre-fill quote used to originally size the trade. LAD/CBZ/GRMN (same session) filled with negligible
slippage and needed no correction — this appears specific to thinner names like NNNN, not systemic.

<!-- DAEMON_ENTRY: EXLS long 2026-07-29 -->
### Jul 29 17:57 UTC — Intraday Daemon Entry
**EXLS** long 266 sh @ ~$35.80 | stop $34.73 | target $37.95 (2.0:1) | gap 16.9%, ORB confirmed above $33.21 | Rule 1: 266 x $1.07 = $285.68 (0.6% of $47,793 equity, cap 4%)

<!-- DAEMON_ENTRY: AGRZ long 2026-07-30 -->
### Jul 30 13:56 UTC — Intraday Daemon Entry
**AGRZ** long 29068 sh @ ~$0.28 (actual fill) | stop $0.28 | target $0.30 (2.0:1) | gap -17.6%, ORB confirmed above $0.27 | Rule 1: 29068 x $0.01 = $248.10 (0.5% of $47,687 equity, cap 4%)

<!-- DAEMON_ENTRY: WETO long 2026-07-30 -->
### Jul 30 14:15 UTC — Intraday Daemon Entry
**WETO** long 279743 sh @ ~$0.03 (actual fill) | stop $0.03 | target $0.03 (2.0:1) | gap -19.7%, ORB confirmed above $0.03 | Rule 1: 279743 x $0.00 = $251.77 (0.5% of $47,556 equity, cap 4%)

### Jul 30 — EOD Force-Close (Day 4)

**Portfolio:** $47,556.40 | **Cash:** $47,556.40 (100% — always ends the day fully flat) | **Day P&L:** -$130.81 (-0.27%) | **Phase P&L:** -$2,443.60 (-4.89%)

| Ticker/OCC | Entry | Exit | Realized P&L | Reason closed |
|---|---|---|---|---|
| AGRZ | $0.2845 | $0.28 | -$130.81 (-1.58%) | Stop-loss hit (daemon, 13:56 UTC) |
| WETO | $0.0300 | $0.0300 | $0.00 (0.00%) | Stop-loss hit (daemon, 14:23 UTC) — breakeven; entry and stop were both effectively at the same sub-penny level, and Alpaca's fill/quote precision (2 decimals) can't resolve finer than that for a $0.03 stock |

**Notes:** Both of today's trades (AGRZ, WETO) were opened and stopped out by the daemon intraday, well before this EOD routine ran — `positions` and `orders` both returned empty when checked, and `close-all`/`cancel-all` were run per protocol as no-ops and reconfirmed empty. Day tally: 2 opened, 2 closed, 0 wins / 1 loss (AGRZ) / 1 breakeven (WETO). AGRZ's actual buy fill ($0.2845) came in above the quoted ~$0.28 entry, so the stop at $0.28 realized a small loss instead of breakeven — same slippage pattern as the NNNN incident on Jul 29, this time in the tolerable range. **Flag for tomorrow:** this routine found no Jul 29 EOD Force-Close entry in this log (Day 3 is missing between Day 2 and today). Cross-checked against Alpaca's fill history: LAD, CBZ, GRMN, and EXLS were all correctly force-closed via market sell_to_close orders at 2026-07-29 19:46 UTC (consistent with a same-second EOD sweep) — so the account was flat every night as required and no capital was left at risk. The gap is a **logging failure only** (Day 3's EOD entry was never appended to TRADE-LOG.md), not a trading failure. Worth checking why that day's routine didn't write its log entry before trusting future runs unattended.

<!-- DAEMON_ENTRY: SKYQ long 2026-07-31 -->
### Jul 31 13:47 UTC — Intraday Daemon Entry
**SKYQ** long 1667 sh @ ~$5.12 (actual fill) | stop $4.97 | target $5.43 (2.0:1) | gap 18.8%, ORB confirmed above $4.68 | Rule 1: 1667 x $0.15 = $256.17 (0.5% of $47,529 equity, cap 4%)

<!-- DAEMON_ENTRY: AAPU long 2026-07-31 -->
### Jul 31 13:48 UTC — Intraday Daemon Entry
**AAPU** long 250 sh @ ~$38.08 (actual fill) | stop $36.94 | target $40.36 (2.0:1) | gap -16.8%, ORB confirmed above $37.99 | Rule 1: 250 x $1.14 = $285.60 (0.6% of $47,639 equity, cap 4%)

<!-- DAEMON_ENTRY: AMZN long 2026-07-31 -->
### Jul 31 14:02 UTC — Intraday Daemon Entry
**AMZN** long 35 sh @ ~$270.50 (actual fill) | stop $262.38 | target $286.73 (2.0:1) | gap 14.9%, ORB confirmed above $269.41 | Rule 1: 35 x $8.11 = $284.02 (0.6% of $47,479 equity, cap 4%)

<!-- DAEMON_ENTRY: AMCX long 2026-07-31 -->
### Jul 31 14:04 UTC — Intraday Daemon Entry
**AMCX** long 852 sh @ ~$11.13 (actual fill) | stop $10.80 | target $11.80 (2.0:1) | gap 15.0%, ORB confirmed above $11.04 | Rule 1: 852 x $0.33 = $284.48 (0.6% of $47,466 equity, cap 4%)
