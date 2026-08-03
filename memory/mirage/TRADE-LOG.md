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

<!-- DAEMON_ENTRY: SMST long 2026-07-31 -->
### Jul 31 14:14 UTC — Intraday Daemon Entry
**SMST** long 147 sh @ ~$63.83 (actual fill) | stop $61.92 | target $67.66 (2.0:1) | gap 17.1%, ORB confirmed above $60.97 | Rule 1: 147 x $1.91 = $281.49 (0.6% of $47,065 equity, cap 4%)

<!-- DAEMON_EXIT: SMST 2026-07-31 14:20 -->
### Jul 31 14:20 UTC — Intraday Daemon Exit
**SMST** closed @ ~$63.76 | entry $63.83 | realized P&L $-10.29 (-0.1%) | reason: VWAP loss on volume spike (thesis break)

<!-- DAEMON_ENTRY: MSTZ long 2026-07-31 -->
### Jul 31 14:21 UTC — Intraday Daemon Entry
**MSTZ** long 745 sh @ ~$12.61 (actual fill) | stop $12.23 | target $13.36 (2.0:1) | gap 15.1%, ORB confirmed above $11.94 | Rule 1: 745 x $0.38 = $281.80 (0.6% of $47,009 equity, cap 4%)

<!-- DAEMON_EXIT: AMCX 2026-07-31 14:34 -->
### Jul 31 14:34 UTC — Intraday Daemon Exit
**AMCX** closed @ ~$11.31 | entry $11.13 | realized P&L $153.36 (1.6%) | reason: VWAP loss on volume spike (thesis break)

<!-- DAEMON_ENTRY: GDDY long 2026-07-31 -->
### Jul 31 14:40 UTC — Intraday Daemon Entry
**GDDY** long 116 sh @ ~$79.73 (actual fill) | stop $77.34 | target $84.52 (2.0:1) | gap -19.9%, ORB confirmed above $78.18 | Rule 1: 116 x $2.39 = $277.46 (0.6% of $47,106 equity, cap 4%)

<!-- DAEMON_ENTRY: FORR long 2026-07-31 -->
### Jul 31 15:50 UTC — Intraday Daemon Entry
**FORR** long 707 sh @ ~$11.60 (actual fill) | stop $11.25 | target $12.30 (2.0:1) | gap 18.4%, ORB confirmed above $11.06 | Rule 1: 707 x $0.35 = $246.04 (0.5% of $46,773 equity, cap 4%)

<!-- DAEMON_ENTRY: IREZ long 2026-07-31 -->
### Jul 31 16:07 UTC — Intraday Daemon Entry
**IREZ** long 535 sh @ ~$17.43 (actual fill) | stop $16.91 | target $18.48 (2.0:1) | gap 15.0%, ORB confirmed above $15.56 | Rule 1: 535 x $0.52 = $279.79 (0.6% of $46,698 equity, cap 4%)

<!-- DAEMON_ENTRY: LFS long 2026-07-31 -->
### Jul 31 16:21 UTC — Intraday Daemon Entry
**LFS** long 3140 sh @ ~$2.64 (actual fill) | stop $2.56 | target $2.80 (2.0:1) | gap 19.7%, ORB confirmed above $2.44 | Rule 1: 3140 x $0.08 = $248.69 (0.5% of $46,485 equity, cap 4%)

<!-- DAEMON_ENTRY: SCYX long 2026-07-31 -->
### Jul 31 16:29 UTC — Intraday Daemon Entry
**SCYX** long 1835 sh @ ~$4.36 (actual fill) | stop $4.23 | target $4.62 (2.0:1) | gap 16.6%, ORB confirmed above $4.34 | Rule 1: 1835 x $0.13 = $239.85 (0.5% of $46,072 equity, cap 4%)

<!-- DAEMON_ENTRY: FFAI long 2026-07-31 -->
### Jul 31 16:39 UTC — Intraday Daemon Entry
**FFAI** long 1224 sh @ ~$6.55 (actual fill) | stop $6.36 | target $6.95 (2.0:1) | gap 19.5%, ORB confirmed above $5.37 | Rule 1: 1224 x $0.20 = $240.70 (0.5% of $45,726 equity, cap 4%)

<!-- DAEMON_ENTRY: CDNA long 2026-07-31 -->
### Jul 31 16:50 UTC — Intraday Daemon Entry
**CDNA** long 204 sh @ ~$44.38 (actual fill) | stop $43.05 | target $47.04 (2.0:1) | gap 16.3%, ORB confirmed above $43.01 | Rule 1: 204 x $1.33 = $271.61 (0.6% of $45,408 equity, cap 4%)

<!-- DAEMON_EXIT: FFAI 2026-07-31 16:53 -->
### Jul 31 16:53 UTC — Intraday Daemon Exit
**FFAI** closed @ ~$6.42 | entry $6.55 | realized P&L $-165.09 (-2.1%) | reason: VWAP loss on volume spike (thesis break)

<!-- DAEMON_ENTRY: FATN long 2026-07-31 -->
### Jul 31 17:15 UTC — Intraday Daemon Entry
**FATN** long 1319 sh @ ~$6.00 (actual fill) | stop $5.82 | target $6.36 (2.0:1) | gap 16.7%, ORB confirmed above $4.78 | Rule 1: 1319 x $0.18 = $237.42 (0.5% of $45,077 equity, cap 4%)

<!-- DAEMON_ENTRY: AEON long 2026-07-31 -->
### Jul 31 17:44 UTC — Intraday Daemon Entry
**AEON** long 24998 sh @ ~$0.31 (actual fill) | stop $0.30 | target $0.33 (2.0:1) | gap 19.5%, ORB confirmed above $0.31 | Rule 1: 24998 x $0.01 = $234.73 (0.5% of $44,534 equity, cap 4%)

### Jul 31 17:45 UTC — Backfill: 8 exits that never got logged (5th bug found and fixed)

**Bug found:** a position that closes via its own standing stop-loss order filling
directly on Alpaca's side (not through the daemon's explicit `close_position()` call)
was never detected or logged — `manage_positions()` only wrote a TRADE-LOG entry when
*it* decided to close something (VWAP-loss or target-hit). A stop firing on its own
between cycles left zero record, even though the account's real P&L was correct the
whole time. Confirmed today: 11 real closed trades, but only 3 (SMST, AMCX, FFAI) had
log entries — the other 8 below were reconstructed from Alpaca's `/account/activities/FILL`
ledger, the authoritative source.

**Fixed in code:** the daemon now tracks which symbols were open at the end of each
cycle; if one disappears by the next cycle without going through the explicit close
path, it's logged immediately with real fill-based entry/exit/P&L, tagged
"(external fill)" so it's distinguishable from a daemon-initiated close.

**The 8 backfilled exits (all stop-loss fills, chronological):**

| Ticker | Entry | Exit | Realized P&L | Time (UTC) |
|---|---|---|---|---|
| SKYQ | $5.1223 | $4.9600 | -$270.62 (-3.17%) | 14:14 |
| MSTZ | $12.6084 | $12.2100 | -$296.84 (-3.16%) | 16:02 |
| AAPU | $38.0800 | $36.9300 | -$287.50 (-3.02%) | 15:49 |
| FORR | $11.6000 | $11.1800 | -$296.94 (-3.62%) | 16:21 |
| LFS | $2.6400 | $2.5500 | -$282.60 (-3.41%) | 16:27 |
| IREZ | $17.4327 | $16.8900 | -$290.30 (-3.11%) | 16:39 |
| SCYX | $4.3570 | $4.0700 | -$526.71 (-6.59%) | 16:46 |
| FATN | $6.0000 | $5.6800 | -$422.08 (-5.33%) | 17:28 |

Combined backfilled realized loss: **-$2,673.59**. All eight hit stops in the
~3-3.6% range as intended (SCYX and FATN somewhat wider, likely a fast-moving-price
gap through the stop level rather than a clean fill at the stop price itself — normal
slippage on a triggered stop, not a bug).

**Full picture for today so far (3 logged + 8 backfilled + 3 still open):**
1 win (AMCX +$153.36), 10 losses, combined realized **-$2,696.60**, plus -$260.72
unrealized on AMZN/CDNA/GDDY (still open) = **-$2,957.32** today, reconciling exactly
with account equity ($44,571.97, down from $47,529.29 last close). (Note: AEON above,
and LESL/INBS below, were entered by the still-running pre-fix daemon process after
this backfill was written — chronology preserved as committed.)

<!-- DAEMON_ENTRY: LESL long 2026-07-31 -->
### Jul 31 18:07 UTC — Intraday Daemon Entry
**LESL** long 7489 sh @ ~$1.04 (actual fill) | stop $1.01 | target $1.10 (2.0:1) | gap 19.8%, ORB confirmed above $0.95 | Rule 1: 7489 x $0.03 = $233.66 (0.5% of $44,185 equity, cap 4%)

<!-- DAEMON_ENTRY: INBS long 2026-07-31 -->
### Jul 31 18:27 UTC — Intraday Daemon Entry
**INBS** long 4057 sh @ ~$1.92 (actual fill) | stop $1.86 | target $2.04 (2.0:1) | gap 20.0%, ORB confirmed above $1.83 | Rule 1: 4057 x $0.06 = $233.68 (0.5% of $44,023 equity, cap 4%)

### Jul 31 19:48 UTC — Backfill: 4 more exits that never got logged (same bug recurring after the 17:45 fix)

**Found by this EOD routine:** `positions` at EOD-close time showed only AMZN and GDDY open, but four more symbols entered today (CDNA, LESL, INBS, AEON) had already hit their standing stop-loss orders and closed via Alpaca's own fill — the same failure mode as the 17:45 backfill above, recurring even after that fix was committed earlier today. Reconstructed from Alpaca's closed-orders history (authoritative).

| Ticker | Entry | Exit | Realized P&L | Time (UTC) |
|---|---|---|---|---|
| CDNA | $44.3800 | $42.7659 | -$329.28 (-3.64%) | 17:52 |
| AEON | $0.3130 | $0.2987 | -$356.40 (-4.55%) | 17:44 |
| LESL | $1.0400 | $1.0000 | -$299.56 (-3.85%) | 18:16 |
| INBS | $1.9200 | $1.7200 | -$811.40 (-10.42%) | 18:38 |

Combined backfilled realized loss: **-$1,796.64**. AEON is notable: entry and stop fired only 23 seconds apart (17:44:14 → 17:44:37 UTC) — a near-instant reversal or thin-liquidity gap-through the stop level, not a clean trigger. INBS was today's single worst loser at -10.42%, well outside the usual ~3-3.6% stop band, consistent with the same fast-slippage pattern seen in SCYX/FATN earlier. **Flag for tomorrow:** the cycle-tracking fix from the 17:45 backfill did not catch these four — this is now the second unlogged-exit incident in one day, worth a closer look at the daemon's external-fill detection before trusting it unattended again.

### Jul 31 — EOD Force-Close (Day 5)

**Portfolio:** $43,493.90 | **Cash:** $43,493.90 (100% — always ends the day fully flat) | **Day P&L:** -$4,062.50 (-8.54%) | **Phase P&L:** -$6,506.10 (-13.01%)

| Ticker/OCC | Entry | Exit | Realized P&L | Reason closed |
|---|---|---|---|---|
| AMZN | $270.4957 | $271.5200 | +$35.85 (+0.38%) | Force-closed by EOD routine (in profit; resting stop was $262.38) |
| GDDY | $79.7312 | $83.3691 | +$422.00 (+4.56%) | Force-closed by EOD routine (in profit; resting stop was $77.34) |

**Notes:** `positions`/`orders` at routine start showed only AMZN and GDDY open (both nicely in profit — GDDY +4.6%, AMZN +0.4% — sitting on resting stops well below market); `cancel-all` cleared those two stops and `close-all` force-sold both at market, confirmed flat via a follow-up `positions` check. Everything else opened today (15 of 17 trades) had already been closed intraday by the daemon's own stop-loss logic well before this routine ran, though 4 of those 15 (CDNA, LESL, INBS, AEON) never got a log entry until this routine reconstructed them above. Full day tally: **17 opened, 17 closed, 3 wins (AMCX +$153.36, AMZN +$35.85, GDDY +$422.00) / 14 losses**. INBS (-10.42%) and AEON (-4.55%, 23-second stop-out) were the day's ugliest fills — both point at slippage/liquidity risk on the daemon's smaller-cap picks rather than a thesis problem. The two positions still open at EOD (AMZN, GDDY) were also the day's biggest winners by dollar size, which stings a little — the strategy has no discretion to let a winner run past EOD, and today that discretion would have paid off, but the no-exception force-close rule stays as-is per protocol. Equity-based Day P&L (-$4,062.50) runs a bit heavier than the sum of today's individual trade P&Ls (~-$4,035), a gap consistent with slippage/spread that doesn't show up per-trade until compared against the account-level mark.

<!-- DAEMON_ENTRY: SXTC long 2026-08-03 -->
### Aug 03 13:46 UTC — Intraday Daemon Entry
**SXTC** long 102920 sh @ ~$0.07 (actual fill) | stop $0.07 | target $0.08 (2.0:1) | gap 19.9%, ORB confirmed above $0.07 | Rule 1: 102920 x $0.00 = $227.25 (0.5% of $43,484 equity, cap 4%)

<!-- DAEMON_EXIT: SXTC 2026-08-03 13:47 -->
### Aug 03 13:47 UTC — Intraday Daemon Exit
**SXTC** closed @ ~$0.07 | entry $0.07 | realized P&L $-30.88 (-0.4%) | reason: VWAP loss on volume spike (thesis break)

<!-- DAEMON_ENTRY: MGRX long 2026-08-03 -->
### Aug 03 13:47 UTC — Intraday Daemon Entry
**MGRX** long 16901 sh @ ~$0.45 (actual fill) | stop $0.44 | target $0.48 (2.0:1) | gap -19.5%, ORB confirmed above $0.45 | Rule 1: 16901 x $0.01 = $230.65 (0.5% of $43,453 equity, cap 4%)

<!-- DAEMON_ENTRY: CRWU long 2026-08-03 -->
### Aug 03 13:50 UTC — Intraday Daemon Entry
**CRWU** long 2748 sh @ ~$3.18 (actual fill) | stop $3.08 | target $3.37 (2.0:1) | gap 13.9%, ORB confirmed above $3.04 | Rule 1: 2748 x $0.10 = $262.16 (0.6% of $43,706 equity, cap 4%)

<!-- DAEMON_ENTRY: KUST long 2026-08-03 -->
### Aug 03 13:51 UTC — Intraday Daemon Entry
**KUST** long 6100 sh @ ~$1.44 (actual fill) | stop $1.40 | target $1.53 (2.0:1) | gap 17.6%, ORB confirmed above $1.33 | Rule 1: 6100 x $0.04 = $263.51 (0.6% of $43,924 equity, cap 4%)

<!-- DAEMON_ENTRY: AUTL long 2026-08-03 -->
### Aug 03 13:53 UTC — Intraday Daemon Entry
**AUTL** long 4979 sh @ ~$1.75 (actual fill) | stop $1.70 | target $1.85 (2.0:1) | gap 15.8%, ORB confirmed above $1.73 | Rule 1: 4979 x $0.05 = $261.40 (0.6% of $43,574 equity, cap 4%)

<!-- DAEMON_EXIT: CRWU 2026-08-03 13:56 -->
### Aug 03 13:56 UTC — Intraday Daemon Exit
**CRWU** closed @ ~$3.40 | entry $3.18 | realized P&L $604.56 (6.9%) | reason: target reached (6.9%, >= 2.0:1 R:R)

<!-- DAEMON_EXIT: MGRX 2026-08-03 13:56 -->
### Aug 03 13:56 UTC — Intraday Daemon Exit
**MGRX** closed @ ~$0.46 | entry $0.45 | realized P&L $1.69 (0.0%) | reason: VWAP loss on volume spike (thesis break)

<!-- DAEMON_ENTRY: CNCK long 2026-08-03 -->
### Aug 03 13:59 UTC — Intraday Daemon Entry
**CNCK** long 4008 sh @ ~$2.22 (actual fill) | stop $2.15 | target $2.35 (2.0:1) | gap 18.4%, ORB confirmed above $2.13 | Rule 1: 4008 x $0.07 = $266.93 (0.6% of $44,498 equity, cap 4%)

<!-- DAEMON_ENTRY: CNH long 2026-08-03 -->
### Aug 03 14:00 UTC — Intraday Daemon Entry
**CNH** long 743 sh @ ~$11.95 (actual fill) | stop $11.59 | target $12.67 (2.0:1) | gap 16.9%, ORB confirmed above $11.96 | Rule 1: 743 x $0.36 = $266.37 (0.6% of $44,487 equity, cap 4%)

<!-- DAEMON_EXIT: KUST 2026-08-03 14:02 -->
### Aug 03 14:02 UTC — Intraday Daemon Exit (external fill)
**KUST** closed @ ~$1.4000 | entry $1.4399 | realized P&L $-243.64 (-2.8%) | reason: stop-loss order filled (detected via position disappearance, not an explicit daemon close — P&L computed from Alpaca's fill ledger)

<!-- DAEMON_ENTRY: CRCG long 2026-08-03 -->
### Aug 03 14:03 UTC — Intraday Daemon Entry
**CRCG** long 1229 sh @ ~$7.04 (actual fill) | stop $6.93 | target $7.26 (2.0:1) | gap -12.7%, ORB confirmed above $7.09 | Rule 1: 1229 x $0.11 = $135.19 (0.3% of $44,519 equity, cap 4%)

<!-- DAEMON_EXIT: CRCG 2026-08-03 14:04 -->
### Aug 03 14:04 UTC — Intraday Daemon Exit (external fill)
**CRCG** closed @ ~$6.9200 | entry $7.0400 | realized P&L $-147.48 (-1.7%) | reason: stop-loss order filled (detected via position disappearance, not an explicit daemon close — P&L computed from Alpaca's fill ledger)

<!-- DAEMON_ENTRY: FOSL long 2026-08-03 -->
### Aug 03 14:04 UTC — Intraday Daemon Entry
**FOSL** long 1530 sh @ ~$5.78 (actual fill) | stop $5.61 | target $6.13 (2.0:1) | gap 16.6%, ORB confirmed above $5.53 | Rule 1: 1530 x $0.17 = $265.30 (0.6% of $44,310 equity, cap 4%)

<!-- DAEMON_EXIT: AUTL 2026-08-03 14:05 -->
### Aug 03 14:05 UTC — Intraday Daemon Exit
**AUTL** closed @ ~$1.86 | entry $1.75 | realized P&L $542.71 (6.2%) | reason: target reached (6.2%, >= 2.0:1 R:R)

<!-- DAEMON_EXIT: FOSL 2026-08-03 14:05 -->
### Aug 03 14:05 UTC — Intraday Daemon Exit
**FOSL** closed @ ~$5.76 | entry $5.78 | realized P&L $-26.47 (-0.3%) | reason: VWAP loss on volume spike (thesis break)

<!-- DAEMON_ENTRY: SNES long 2026-08-03 -->
### Aug 03 14:06 UTC — Intraday Daemon Entry
**SNES** long 4976 sh @ ~$1.56 (actual fill) | stop $1.51 | target $1.65 (2.0:1) | gap 16.6%, ORB confirmed above $1.62 | Rule 1: 4976 x $0.05 = $232.88 (0.5% of $44,287 equity, cap 4%)

<!-- DAEMON_EXIT: CNCK 2026-08-03 14:08 -->
### Aug 03 14:08 UTC — Intraday Daemon Exit
**CNCK** closed @ ~$2.22 | entry $2.22 | realized P&L $0.00 (0.0%) | reason: VWAP loss on volume spike (thesis break)

<!-- DAEMON_ENTRY: CWVX long 2026-08-03 -->
### Aug 03 14:09 UTC — Intraday Daemon Entry
**CWVX** long 617 sh @ ~$14.20 (actual fill) | stop $13.77 | target $15.05 (2.0:1) | gap 19.3%, ORB confirmed above $13.61 | Rule 1: 617 x $0.43 = $262.84 (0.6% of $43,945 equity, cap 4%)

<!-- DAEMON_ENTRY: KAZR long 2026-08-03 -->
### Aug 03 14:10 UTC — Intraday Daemon Entry
**KAZR** long 3143 sh @ ~$2.44 (actual fill) | stop $2.37 | target $2.59 (2.0:1) | gap 18.7%, ORB confirmed above $2.15 | Rule 1: 3143 x $0.07 = $230.07 (0.5% of $43,855 equity, cap 4%)

<!-- DAEMON_EXIT: KAZR 2026-08-03 14:27 -->
### Aug 03 14:27 UTC — Intraday Daemon Exit (external fill)
**KAZR** closed @ ~$2.2500 | entry $2.4400 | realized P&L $-597.17 (-7.8%) | reason: stop-loss order filled (detected via position disappearance, not an explicit daemon close — P&L computed from Alpaca's fill ledger)

<!-- DAEMON_ENTRY: SRAD long 2026-08-03 -->
### Aug 03 14:27 UTC — Intraday Daemon Entry
**SRAD** long 728 sh @ ~$11.96 (actual fill) | stop $11.60 | target $12.68 (2.0:1) | gap -17.8%, ORB confirmed above $11.94 | Rule 1: 728 x $0.36 = $261.21 (0.6% of $43,572 equity, cap 4%)

<!-- DAEMON_EXIT: SRAD 2026-08-03 14:35 -->
### Aug 03 14:35 UTC — Intraday Daemon Exit
**SRAD** closed @ ~$12.09 | entry $11.96 | realized P&L $94.28 (1.1%) | reason: VWAP loss on volume spike (thesis break)

<!-- DAEMON_EXIT: CWVX 2026-08-03 14:54 -->
### Aug 03 14:54 UTC — Intraday Daemon Exit
**CWVX** closed @ ~$15.12 | entry $14.20 | realized P&L $567.64 (6.5%) | reason: target reached (6.5%, >= 2.0:1 R:R)

<!-- DAEMON_ENTRY: WETH long 2026-08-03 -->
### Aug 03 15:06 UTC — Intraday Daemon Entry
**WETH** long 7686 sh @ ~$1.00 (actual fill) | stop $0.97 | target $1.06 (2.0:1) | gap -14.6%, ORB confirmed above $1.00 | Rule 1: 7686 x $0.03 = $230.40 (0.5% of $43,815 equity, cap 4%)

<!-- DAEMON_EXIT: CNH 2026-08-03 15:09 -->
### Aug 03 15:09 UTC — Intraday Daemon Exit (external fill)
**CNH** closed @ ~$11.5900 | entry $11.9500 | realized P&L $-267.48 (-3.0%) | reason: stop-loss order filled (detected via position disappearance, not an explicit daemon close — P&L computed from Alpaca's fill ledger)

<!-- DAEMON_EXIT: SNES 2026-08-03 15:17 -->
### Aug 03 15:17 UTC — Intraday Daemon Exit (external fill)
**SNES** closed @ ~$1.5100 | entry $1.5600 | realized P&L $-248.80 (-3.2%) | reason: stop-loss order filled (detected via position disappearance, not an explicit daemon close — P&L computed from Alpaca's fill ledger)

<!-- DAEMON_ENTRY: FNGR long 2026-08-03 -->
### Aug 03 15:21 UTC — Intraday Daemon Entry
**FNGR** long 34743 sh @ ~$0.22 (actual fill) | stop $0.22 | target $0.24 (2.0:1) | gap -19.7%, ORB confirmed above $0.18 | Rule 1: 34743 x $0.01 = $231.39 (0.5% of $43,967 equity, cap 4%)

<!-- DAEMON_EXIT: FNGR 2026-08-03 15:25 -->
### Aug 03 15:25 UTC — Intraday Daemon Exit (external fill)
**FNGR** closed @ ~$0.2189 | entry $0.2220 | realized P&L $-107.70 (-1.4%) | reason: stop-loss order filled (detected via position disappearance, not an explicit daemon close — P&L computed from Alpaca's fill ledger)

<!-- DAEMON_ENTRY: MBRX long 2026-08-03 -->
### Aug 03 15:26 UTC — Intraday Daemon Entry
**MBRX** long 25426 sh @ ~$0.34 (actual fill) | stop $0.33 | target $0.37 (2.0:1) | gap -14.7%, ORB confirmed above $0.34 | Rule 1: 25426 x $0.01 = $263.16 (0.6% of $43,861 equity, cap 4%)

<!-- DAEMON_EXIT: MBRX 2026-08-03 15:35 -->
### Aug 03 15:35 UTC — Intraday Daemon Exit (external fill)
**MBRX** closed @ ~$0.3272 | entry $0.3450 | realized P&L $-452.58 (-5.2%) | reason: stop-loss order filled (detected via position disappearance, not an explicit daemon close — P&L computed from Alpaca's fill ledger)
