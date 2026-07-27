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
market close, with no exceptions.** This isn't a target — it's mandatory.
The EOD-close routine force-closes anything still open at ~2:45pm Chicago
(15 min before the 3:00pm close) regardless of P&L, regardless of whether
a thesis "looks like it just needs one more day." A position held
overnight is a bug, not a strategic choice.

### Why this exists, and an honest limitation to know
Mirage (like Oasis) only "wakes up" a few times a day — a morning entry
check, a midday check, and the mandatory EOD close. It is **not** truly
watching the market tick-by-tick between those times. This means Mirage
cannot react in real time to something happening at, say, 10:15am if its
next check-in isn't until noon. The real protection between check-ins is
the **stop-loss order placed live with Alpaca at entry** (see below) —
that order sits on the exchange and can trigger any time during market
hours, independent of when Mirage's own reasoning next runs. Never open a
position without that live stop in place immediately on fill.

## Position sizing & risk
1. **HARD CAP, never bends:** no single trade may risk more than 8% of
   CURRENT Mirage equity (position size x stop distance for stocks;
   premium paid for long options). At the $50,000 start, that's $4,000.
2. Max 4 concurrent positions (day trading works better with focus, not
   8 simultaneous bets you can't watch closely).
3. Max 40% of equity notional per position — subject to the 8% loss cap
   above, which will usually bind first.
4. No weekly or daily trade-count cap — multiple trades per day are fine
   when setups justify it, but every one still needs a documented catalyst
   and the Rule 1 loss-cap math shown explicitly.
5. Target 50-80% capital deployed during the trading day — lower than
   Oasis's target, because day trading needs cash in reserve for
   same-day opportunities and because everything unwinds by the close
   anyway (no benefit to being 100% deployed at 8:31am if nothing else
   qualifies until 11am).

## Stock rules
- **Stop: 2-3% below entry** (much tighter than Oasis's 7-10% — day
  trades need less room since the whole thesis plays out in hours, not
  days). Place as a real stop order (not trailing — trailing stops add
  complexity for something that's getting force-closed in hours anyway;
  a fixed stop is simpler and sufficient for a same-day hold).
- Target: minimum 2:1 reward-to-risk, same discipline as Oasis.
- If a position is up meaningfully (+3-5%) well before the EOD close
  window, consider taking profit rather than waiting for the mandatory
  close to do it — a deliberate exit beats a forced one when you're
  already ahead.

## Options rules
- **Minimum 3 DTE at entry** — deliberately NOT 0DTE/1DTE. Same-day
  expiration options have extreme gamma/theta swings that turn a same-day
  hold into a lottery ticket rather than a sized bet; a few days of buffer
  keeps the position's value behavior sane for an intraday hold even
  though it will be closed same-day regardless.
- Only long calls/puts (buy-to-open) for now — no verticals, no naked
  single-leg, no covered calls/CSPs on this sleeve. Day trading is already
  a new, unproven strategy for this bot; keep the options side simple
  (defined-risk, max loss = premium paid) until there's a track record.
- Max loss = premium paid, must satisfy the 8%-of-equity Rule 1 cap.
- Close by end of day regardless of P&L — same mandatory rule as stocks.
  If it's down badly, cut it well before the close, don't wait for the
  force-close routine to do it at the last minute.

## What counts as a catalyst (day-trading specific)
Multi-day fundamental themes (sector momentum over a month, YTD leadership)
are Oasis's domain, not Mirage's — by the time a monthly trend matters,
it's not a day-trade signal. Mirage's catalysts should be same-day and
concrete:
- A confirmed earnings reaction that morning (beat/miss + price holding
  the gap, re-validated with a live quote, not just the pre-market print)
- Unusual volume/news specific to that day (an FDA approval, a contract
  win, an analyst up/downgrade with a stated reason)
- A confirmed gap at the open with a stated reason — not just "it gapped,"
  but why, and whether the gap is holding or fading in the first minutes
  of trading
- Economic data (CPI, jobs, Fed announcements) released that morning,
  with a clear, statable direction of reaction

If nothing that specific and same-day exists, the correct call is no
trade that day — same "bias toward action, but only when something real
clears the bar" philosophy as Oasis, just calibrated to intraday signals
instead of multi-week ones.

## Entry checklist (every trade)
- What is the specific, same-day catalyst? (see above — must be dated
  today, not "this has been trending")
- Confirmed with a live quote at entry time, not a stale/pre-market price
- Stop level (2-3% stocks) and target (min 2:1 R:R)
- The Rule 1 max-loss-at-8%-of-equity calculation, shown explicitly
- For options: DTE (>=3), defined-risk confirmation (long calls/puts only)

## What happens at each check-in
- **Morning entry:** research today's specific catalysts, size and place
  any qualifying trades, immediately place real stop-loss orders.
- **Midday check:** re-evaluate open positions (take profit early if
  already well ahead; cut early if the thesis has clearly broken — don't
  wait for the stop or the forced close if something's obviously wrong).
  Can also open a new position here if a fresh same-day catalyst appears
  that wasn't there this morning.
- **EOD close (mandatory, ~2:45pm Chicago):** close every remaining open
  position — market order, no exceptions — cancel any remaining stop
  orders, log the day's realized results.

## Learning loop
Because Mirage force-closes everything daily, it will have **real,
realized closed trades** far faster than Oasis (which is still sitting on
unrealized swing positions). Use that: track win rate and average
win/loss size explicitly once there's a few days of data, and flag to a
human if a specific pattern (e.g., a particular catalyst type, or entries
after a certain time of day) is producing repeated losses — this is a new,
unproven strategy and the first couple of weeks are as much about finding
out if this approach has real edge as they are about making money.
