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
