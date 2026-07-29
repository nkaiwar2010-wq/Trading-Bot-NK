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

## Operating model: continuous daemon (v3, 2026-07-27)
Mirage's entries and position management now run as a **continuous
GitHub Actions daemon** (`scripts/mirage_daemon.py`), not a Claude Code
cloud routine. Claude Code's routine scheduler (`RemoteTrigger`) has a
hard platform floor of one firing per hour — that was v2's ceiling, and
it's still too slow for real day-trading. The daemon works around this
by moving outside Claude Code's routine system entirely: a single
GitHub Actions job starts at market open and loops in-process, polling
Alpaca every ~60 seconds until a safety cutoff before the mandatory
EOD-close, holding state (which symbols were already attempted today)
in memory for the whole session instead of losing it between fires like
v1/v2 did.

The daemon is **deterministic code, not an LLM call per decision** — the
Gap-and-Go / Opening-Range-Breakout / VWAP rules below are fully
specified, so a script executes them directly against Alpaca rather than
an agent re-reasoning every cycle. This is a deliberate scope cut for v3:
**stock-only, long-only** (movers/most-actives are stock screeners
anyway; options can be added back once this is proven). Any existing
option position is left for the hourly-cadence tooling / EOD-close to
handle, not touched by the daemon.
- Runs 8:30am Chicago (market open) through a hard exit around 2:30pm
  Chicago, stopping new entries at 2:15pm — safely under GitHub Actions'
  6-hour job limit and with buffer before the separate, still-mandatory
  EOD-close routine at 2:45pm, which remains the hard backstop for the
  no-overnight-holds rule regardless of what the daemon did or didn't do.
- Commits to TRADE-LOG.md only on an actual entry or exit, tagged with a
  machine-parseable `<!-- DAEMON_ENTRY: SYMBOL long YYYY-MM-DD -->` /
  `<!-- DAEMON_EXIT: ... -->` marker so a mid-day restart can recover
  which symbols were already attempted without re-reading the whole log.
- Claude's role narrows to what it's good at: the nightly Evening
  Research routine (still WebSearch-based, still builds tomorrow's
  watchlist) and periodic strategy review — not live tick-by-tick
  execution.

### Why this replaced the hourly-scan model
v2 (hourly Claude Code routine) was itself a replacement for v1's 3x/day
WebSearch-catalyst model, which failed on quiet news days (confirmed
2026-07-27: two HOLD decisions in a row
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
   - Gap or intraday move between 3% and 20% (either direction; short the
     losers side is a future extension — for now, long-only, see below).
     The 20% ceiling was added after day-1 live data (2026-07-27): both
     losing trades that day had already gapped 85.8% and 64.6% before
     entry — an already-extended move is a materially different, worse
     trade than a fresh breakout, prone to reversal right after entry.
     20% is a judgment call pending more data, not a statistically
     derived line from a 4-trade sample.
   - Relative volume materially elevated (treat "most-actives" appearance
     itself as the RVOL confirmation signal — Alpaca doesn't expose a raw
     RVOL multiple directly, so presence in the most-actives list by
     volume is the proxy)
   - **Screen the top 50 of movers/most-actives, not top 10** (fixed
     2026-07-29): confirmed live on two separate real trading days that
     the top ~10 gainers/losers are dominated entirely by extreme
     penny-stock/warrant moves (40-105%+) that fail the 20% ceiling
     anyway. Legitimate 3-20% candidates in real, liquid names (e.g. LAD,
     GRMN, EXLS, NEO on 2026-07-29) sit just below the top 10 and were
     being missed completely — zero trades on two consecutive real
     trading days despite real candidates existing, purely from not
     looking far enough down the list.
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

## Options rules (currently dormant — see v3 scope cut above)
The daemon that runs Mirage as of v3 is stock-only; nothing currently
opens new option positions on this sleeve. These rules stay documented
for when options are added back:
- **Minimum 3 DTE at entry** — deliberately NOT 0DTE/1DTE.
- Only long calls (buy-to-open) for now, matching the long-only entry
  model above — no verticals, no naked single-leg, no covered calls/CSPs
  on this sleeve.
- Max loss = premium paid, must satisfy the 8%-of-equity Rule 1 cap.
- Close by end of day regardless of P&L — same mandatory rule as stocks.
  Options have no native stop order on Alpaca — the -50%-premium close
  plan must be checked continuously for any open option position.

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

## What happens each day
- **Intraday Daemon (continuous, ~8:30am-2:30pm Chicago):** a single
  GitHub Actions job, not a Claude Code routine. Manages open positions
  (VWAP-loss exit, target hit) and screens/trades new entries every
  ~60 seconds, stock-only. Commits to TRADE-LOG.md only on an actual
  entry or exit.
- **Evening Research (after close, ~4pm Chicago, Claude Code routine):**
  WebSearch-based, research-only, no trading. Builds a "watchlist for
  tomorrow" entry in RESEARCH-LOG.md (upcoming earnings before tomorrow's
  open, overnight news, economic calendar) that the daemon can factor in.
  Always commits — the one guaranteed daily log entry even on a quiet
  night.
- **EOD close (mandatory, ~2:45pm Chicago, Claude Code routine):** close
  every remaining open position — market order, no exceptions — cancel
  any remaining stop orders, log the day's realized results. This is the
  hard backstop for the no-overnight-holds rule regardless of what the
  daemon did or didn't do, unchanged since v1.

## Learning loop
Because Mirage force-closes everything daily, it will have real, realized
closed trades fast. Track win rate and average win/loss size explicitly
once there's a few days of data, and flag to a human if a specific pattern
(e.g., a particular time-of-day, or entries right after a screener hit
without a clean ORB confirmation) is producing repeated losses — this is a
new, unproven strategy and the first couple of weeks are as much about
finding out if this approach has real edge as they are about making money.
