# Trading Strategy — Mirage (Day-Trading Sleeve)

## What Mirage is
Mirage is a **separate bot, separate Alpaca paper account, separate capital**
from Oasis. Same repo, same underlying Claude Code infrastructure, same
overall experiment — but a distinct strategy, distinct memory, and zero
shared risk with Oasis. Mirage never reads Oasis's memory files
(`memory/TRADING-STRATEGY.md`, `memory/TRADE-LOG.md`, etc.) and Oasis never
reads Mirage's. Treat them as two independent traders who happen to work
for the same person.

## Capital & Constraints
- Starting capital: $50,000 (Alpaca PAPER TRADING — no real money), account
  PA3ER1AHRYXX
- Platform: Alpaca (options approved Level 3, same as Oasis's account)
- Instruments: stocks and options (same-day round trips only — see below)
- This account has its own `ALPACA_API_KEY`/`ALPACA_SECRET_KEY` set on
  Mirage's own cloud environment. Never use Oasis's credentials here and
  never let Mirage's credentials leak into Oasis's environment.

## THE CORE RULE: no overnight holds, ever
**Every position Mirage opens must be closed the same trading day, before
market close, with no exceptions.** The EOD-close routine force-closes
anything still open at ~2:45pm Chicago (15 min before the 3:00pm close)
regardless of P&L, regardless of whether a thesis "looks like it just needs
one more day." A position held overnight is a bug, not a strategic choice.

## Operating model: near-continuous intraday scan (v2, 2026-07-27)
Mirage runs an **Intraday Scan** every 5 minutes from 8:30am to 2:45pm
Chicago (market open to just before the mandatory EOD close) — roughly 75
check-ins per trading day, plus the EOD-close routine and an after-hours
Evening Research routine. Each scan is a fresh, stateless session (no memory
of the prior scan except what's committed to git) that:
1. Reads today's date and this file for rules.
2. Pulls live account/positions/orders.
3. Manages anything already open (see "Position management" below).
4. If under 4 open positions, screens for a new entry (see "Entry model"
   below) and trades it if it clears every rule.
5. Commits and pushes **only if something changed** (a trade opened,
   a trade closed, a stop adjusted). A pure "scanned, nothing qualified"
   cycle is a silent no-op — no commit. This is deliberate: at ~75
   scans/day, logging every single no-op would flood the trade/research
   logs with noise. Silence between logged entries means "nothing
   happened," not "the bot is broken."

### Why this replaced the old 3-checkpoint model
The original version (morning-entry / midday-check / EOD-close, 3x/day)
relied on WebSearch to find "same-day catalysts." In practice this failed
on quiet news days (confirmed 2026-07-27: two HOLD decisions in a row
because WebSearch cannot see live pre-market/intraday tape — it's a search
engine, not a real-time data feed). The v2 model fixes this by using
**Alpaca's own market-data endpoints** as the primary signal source instead
of news search:
- `bash scripts/alpaca.sh movers [top_n]` — real-time gainers/losers
  (gap detection), resets at market open
- `bash scripts/alpaca.sh most-actives [top_n] [volume|trades]` — real-time
  relative-volume leaders
- `bash scripts/alpaca.sh bars SYM [timeframe] [limit]` — intraday OHLCV
  bars (1Min/5Min/etc.) with VWAP built into each bar

News/WebSearch is now used only in the separate Evening Research routine
(next-day prep, not live trading) — see below. **A same-day news story is
no longer required to trade; a clean, confirmed price-action setup is
sufficient on its own.** This is the one deliberate philosophy change from
v1: Mirage trades what the tape is doing, not what the news says it should
be doing.

## Entry model: Gap-and-Go confirmed by Opening Range Breakout, managed by VWAP
Three techniques, used together (a well-documented combination — the gap
identifies the candidate, the ORB confirms the move is real rather than a
fade, VWAP governs the exit):

1. **Screen** `movers`/`most-actives` for candidates with:
   - Gap or intraday move of at least 3% (either direction; short the
     losers side is a future extension — for now, long-only, see below)
   - Relative volume materially elevated (treat "most-actives" appearance
     itself as the RVOL confirmation signal — Alpaca doesn't expose a raw
     RVOL multiple directly, so presence in the top-10 most-actives list by
     volume is the proxy)
2. **Confirm** with `bash scripts/alpaca.sh bars SYM 5Min 20`:
   - Establish the opening range: the high/low of the first 5-15 minutes
     of trading (the first one to three 5-minute bars after 8:30am
     Chicago).
   - Only enter once price has **closed** a 5-minute bar beyond that range
     in the gap's direction — never enter mid-bar on a wick, wait for the
     confirmed close. This avoids the classic ORB failure mode of entering
     a breakout that immediately fails.
   - One trade per side per symbol per day: if the first breakout attempt
     fails and reverses, do not re-enter the same direction on that symbol
     today.
3. **Manage** using VWAP (the `vwap` field on each bar from the `bars`
   command):
   - A reclaim/rejection of VWAP on rising volume is meaningful; a drift
     across VWAP on thin volume is not — don't treat a low-volume cross as
     a signal either way.
   - If a position loses VWAP on a volume spike after being above it, that
     is an early "thesis broke" signal — exit before waiting for the fixed
     stop or the EOD close to do it.
   - Target: first objective is a retest of the high (long) or low
     (short) of day; take partial/full profit there rather than waiting
     for the forced EOD close if already well ahead.

Long-only for now (calls/long stock; no shorting, no puts on this entry
model yet) — keep the first iteration of a new, unproven strategy simple.
Existing catalyst-based entries (a confirmed earnings reaction, a stated
FDA/contract-win headline) are still valid **in addition to** a technical
setup if one surfaces intraday, but are no longer required to trade.

## Position sizing & risk (unchanged from v1)
1. **HARD CAP, never bends:** no single trade may risk more than 8% of
   CURRENT Mirage equity (position size x stop distance for stocks;
   premium paid for long options). At the $50,000 start, that's $4,000.
2. Max 4 concurrent positions.
3. Max 40% of equity notional per position — subject to the 8% loss cap
   above, which will usually bind first.
4. No weekly or daily trade-count cap — multiple trades per day are fine
   when setups justify it, and the Rule 1 loss-cap math must be shown
   explicitly every time.
5. Target 50-80% capital deployed during the trading day.

## Stock rules
- **Stop: 2-3% below entry**, or the opening-range low/high if that's
  tighter — whichever gives the smaller defined loss while still
  satisfying Rule 1. Place as a real fixed stop order immediately on fill
  (not trailing).
- Target: minimum 2:1 reward-to-risk. First partial at 2:1, remainder
  trails toward the high/low-of-day retest per the VWAP management rule
  above.

## Options rules
- **Minimum 3 DTE at entry** — deliberately NOT 0DTE/1DTE.
- Only long calls (buy-to-open) for now, matching the long-only entry
  model above — no verticals, no naked single-leg, no covered calls/CSPs
  on this sleeve.
- Max loss = premium paid, must satisfy the 8%-of-equity Rule 1 cap.
- Close by end of day regardless of P&L — same mandatory rule as stocks.
  Options have no native stop order on Alpaca — the -50%-premium close
  plan must be checked every scan cycle for any open option position, not
  just at midday/EOD as in v1.

## Entry checklist (every trade)
- Candidate surfaced via `movers` or `most-actives` (or, secondarily, a
  confirmed same-day catalyst)
- Opening range established, and a 5-minute bar has **closed** beyond it
  in the trade direction (not a mid-bar wick)
- Live quote confirms the level at entry time
- Stop level (2-3% or opening-range extreme) and target (min 2:1 R:R)
  defined before the order is placed
- The Rule 1 max-loss-at-8%-of-equity calculation, shown explicitly
- For options: DTE (>=3), long calls only
- Position count check: currently under 4 open positions
- Not a second attempt on the same symbol/side that already failed today

## What happens at each check-in
- **Intraday Scan (every 5 min, 8:30am-2:45pm Chicago):** manage open
  positions first (VWAP-loss exit, thesis break, profit-take, stop
  maintenance), then screen and trade new entries if under 4 positions.
  Commit only if something changed.
- **Evening Research (after close, ~4pm Chicago):** WebSearch-based,
  research-only, no trading. Builds a "watchlist for tomorrow" entry in
  RESEARCH-LOG.md (upcoming earnings before tomorrow's open, overnight
  news, economic calendar) that tomorrow's first Intraday Scan can read
  for a head start. Always commits (this is the one log write per day
  guaranteed to happen even on a totally quiet day).
- **EOD close (mandatory, ~2:45pm Chicago):** close every remaining open
  position — market order, no exceptions — cancel any remaining stop
  orders, log the day's realized results. Unchanged from v1.

## Learning loop
Because Mirage force-closes everything daily, it will have real, realized
closed trades fast. Track win rate and average win/loss size explicitly
once there's a few days of data, and flag to a human if a specific pattern
(e.g., a particular time-of-day, or entries right after a screener hit
without a clean ORB confirmation) is producing repeated losses — this is a
new, unproven strategy and the first couple of weeks are as much about
finding out if this approach has real edge as they are about making money.
