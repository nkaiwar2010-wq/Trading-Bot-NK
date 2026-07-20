# Trading Strategy

## Mission
Maximize risk-adjusted returns — the objective is real money-making
performance, not just beating a benchmark for its own sake. Stocks and
options, paper trading only (Alpaca paper account — no real money) during
this phase. Options, including uncovered/naked single-leg positions, are
permitted specifically to stress-test the bot's risk handling and decision
quality under higher-variance instruments.

This is explicitly a development/proving phase toward a longer-term goal:
turning this into a real passive income source. That means every loss and
every mistake is data, not just a number to shrug off:
- The weekly review (memory/WEEKLY-REVIEW.md) is the primary mechanism for
  this — "what worked / what didn't / key lessons / adjustments" must be
  concrete and specific enough to act on, not generic.
- A rule or sizing/DTE parameter that fails repeatedly (2+ consecutive
  losses attributable to the same root cause) must be flagged for a
  strategy change in TRADING-STRATEGY.md itself, not just noted and
  repeated next week.
- A rule or approach that proves out over 2+ weeks should be reinforced,
  not abandoned for novelty.
- Before ever connecting a live account, this scope (especially
  undefined-risk naked options) must be explicitly revisited — what works
  in a paper-trading stress test does not automatically transfer to real
  capital.

## Capital & Constraints
- Starting capital: ~$100,000 (Alpaca PAPER TRADING — no real money)
- Platform: Alpaca
- Instruments: Stocks AND options (calls, puts, covered calls, cash-secured
  puts, verticals/spreads, and single-leg uncovered/naked calls or puts)
- Options approval level on this account: Level 3 (multi-leg/spreads enabled;
  Alpaca requires every leg of a multi-leg order to be covered within that
  order — naked legs must be submitted as separate single-leg orders)
- PDT limit: 3 day trades per 5 rolling days — N/A above $25k equity, but the
  buy-side gate still checks daytrade_count defensively in case balance ever
  drops near that threshold

## Core Rules (stocks)
1. 75-85% deployed
2. 5-6 positions at a time (stocks + options combined), max 20% of equity
   notional/risk each
3. 10% trailing stop on every stock position as a real GTC order
4. Cut losers at -7% manually
5. Tighten trail: 7% at +15%, 5% at +20%
6. Never within 3% of current price; never move a stop down
7. Max 3 new trades per week (stocks + options combined)
8. Follow sector momentum
9. Exit a sector after 2 consecutive failed trades
10. Patience > activity

## Options Rules
Options move faster and decay on their own (theta), so stock-style
percentage trailing stops don't translate directly. Separate rules apply:

### Allowed strategies
- Long calls / long puts (buy-to-open)
- Covered calls (sell call against owned shares)
- Cash-secured puts (sell put with cash reserved for assignment)
- Vertical spreads / other defined-risk multi-leg (`order_class: "mleg"`,
  every leg covered within the same order — Alpaca's Level 3 requirement)
- Single-leg uncovered/naked calls or puts (submitted as standalone
  single-leg orders, not inside an `mleg` order) — permitted for this
  stress-test phase only, gated by Alpaca's own `options_buying_power`
  check. Never attempt to work around a buying-power rejection (no
  reducing size just to force a fill past a real margin block) — if Alpaca
  rejects it, the trade is skipped and logged, same as any other gate
  failure.

### Position sizing
- Defined-risk trades (long options, verticals, covered calls, cash-secured
  puts): max loss (premium paid, or spread width x contracts x 100, or
  strike x 100 for a csp) capped at 20% of equity — same cap as stocks.
- Undefined-risk trades (naked short calls/puts): cap notional exposure
  (strike price x 100 x contracts) at 20% of equity as a proxy for max
  loss, in addition to whatever Alpaca's margin/buying-power check requires.
- Combined stock + options positions count toward the same 5-6 max open
  positions and 3 new trades/week caps — this is one book, not two.

### Days-to-expiration (DTE) rules
- Do not open a new options position with fewer than 7 DTE (avoid
  gamma/pin risk close to expiration).
- Close or roll any options position within 2 DTE of expiration —
  never hold a short option through expiration/into assignment
  unintentionally, and never let a long option expire worthless without a
  deliberate decision to do so.

### Stop-loss / profit-taking (options)
- Long calls/puts: close at -50% of premium paid. Take profit at +50-100%
  gain (documented target > minimum, don't need a hard cap — use judgment
  same as stock targets).
- Verticals/spreads: close if the spread reaches ~80% of its max possible
  loss. Take profit at ~50-75% of max possible profit.
- Naked short calls/puts: buy-to-close if the option's current value has
  increased 100% from the premium received (i.e., the position is down as
  much as it could ever be up), OR if the underlying breaches the strike
  intraday (assignment risk trigger) — whichever comes first. Never average
  down / add to a losing naked short position.
- Never move a protective adjustment (rolling a spread, adjusting a naked
  short) in a way that increases max loss versus the original entry.

### Entry checklist additions (options, on top of the stock checklist)
- Strike, expiration date, and DTE at entry
- Defined-risk or undefined-risk? (state explicitly)
- If undefined-risk: confirm `options_buying_power` covers Alpaca's
  requirement before attempting the order

## Entry Checklist (stocks)
- Specific catalyst?
- Sector in momentum?
- Stop level (7-10% below entry)
- Target (min 2:1 R:R)
