# Trading Strategy — Oasis

## THE CHALLENGE (current objective — overrides default pacing below)
- Start date: 2026-07-19. Deadline: 2026-08-19 (30 days).
- Target: grow the account by $50,000+ profit (equity >= $150,000 from a
  $100,000 start) by the deadline. This is a real, specific, time-boxed
  target — not an open-ended "beat the market" mission.
- Every research/execution cycle MUST state: days remaining until deadline,
  current equity vs. the $150,000 target, and whether pace is on-track,
  ahead, or behind. If behind pace with the deadline approaching, lean
  toward the more aggressive end of what's allowed below (larger size,
  more concurrent positions) — never toward abandoning the hard per-trade
  loss cap to chase pace. A blown account hits 0% of the target; a
  contained loss leaves runway to keep trying.
- This target requires materially more trade frequency and size than the
  slower "patience > activity" posture below was built for. That posture
  is superseded for the duration of this challenge by the Core Rules in
  this document — read this section first, every cycle.

## Mission
Maximize risk-adjusted returns — the objective is real money-making
performance, not just beating a benchmark for its own sake. Stocks and
options, paper trading only (Alpaca paper account — no real money) during
this phase. Options, including uncovered/naked single-leg positions, are
permitted specifically to stress-test the bot's risk handling and decision
quality under higher-variance instruments, and are one of the primary
tools for hitting the challenge target above given the shorter timeframe.

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
  undefined-risk naked options and the aggressive sizing below) must be
  explicitly revisited — what works in a paper-trading stress test does
  not automatically transfer to real capital.

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

## Core Rules (stocks) — AGGRESSIVE BUT BOUNDED, for the challenge above
1. Target 85-100% capital deployed (raised from the prior 75-85% — cash
   sitting idle doesn't hit a 30-day target).
2. Up to 8 positions at a time (stocks + options combined). Max 30% of
   equity notional per position (raised from 20%) — but every position's
   ACTUAL size must also satisfy Rule 3 below.
3. HARD CAP, no exceptions: no single trade may risk more than 8% of
   CURRENT equity, computed from position size x stop distance (stocks) or
   position size x max-defined-loss (options — see Options Rules). Size
   the position to fit this cap, not the other way around. This is the one
   rule that never bends regardless of pace or deadline pressure.
4. 10% trailing stop on every stock position as a real GTC order.
5. Cut losers at -7% manually if the trailing stop hasn't already closed it.
6. Tighten trail: 7% at +15%, 5% at +20%.
7. Never within 3% of current price; never move a stop down.
8. NO weekly trade-count cap (the prior "max 3/week" is removed for the
   duration of the challenge — it directly conflicts with the target).
   Multiple trades per day are fine when setups justify it. Every trade
   still requires a documented catalyst and must pass Rule 3's loss cap.
9. Follow sector momentum; volatile, event-driven days (CPI, earnings,
   geopolitical headlines) are trade TRIGGERS to evaluate, not blanket
   reasons to sit out — the moves needed to hit this target come from
   volatility, not from waiting for it to pass.
10. Exit a sector after 2 consecutive failed trades in it.
11. Bias toward action: sitting in cash/HOLD is only the right call when
    literally nothing passes the catalyst + Rule 3 loss-cap check that
    cycle — not a default preference. Report explicitly why nothing
    qualified if the decision is HOLD.

## Options Rules
Options move faster and decay on their own (theta), so stock-style
percentage trailing stops don't translate directly. Separate rules apply.
Options are a primary lever for the challenge target — use them
deliberately, not as an afterthought to stocks.

### Allowed strategies
- Long calls / long puts (buy-to-open)
- Covered calls (sell call against owned shares)
- Cash-secured puts (sell put with cash reserved for assignment)
- Vertical spreads / other defined-risk multi-leg (`order_class: "mleg"`,
  every leg covered within the same order — Alpaca's Level 3 requirement)
- Single-leg uncovered/naked calls or puts (submitted as standalone
  single-leg orders, not inside an `mleg` order) — gated by Alpaca's own
  `options_buying_power` check. Never attempt to work around a buying-power
  rejection (no reducing size just to force a fill past a real margin
  block) — if Alpaca rejects it, the trade is skipped and logged, same as
  any other gate failure.

### Position sizing (all options — this is where Core Rule 3 applies)
- Defined-risk trades (long options, verticals, covered calls, cash-secured
  puts): size so max loss (premium paid, or spread width x contracts x
  100, or strike x 100 for a csp) is <= 8% of current equity. Up to 30% of
  equity in notional/premium is allowed by Rule 2, but the 8% max-loss cap
  from Rule 3 governs whenever it's more restrictive — it almost always
  will be for anything other than a small-premium long option.
- Undefined-risk trades (naked short calls/puts): size the contract count
  so that a loss equal to 2x the premium received (the exit-rule trigger
  below) does NOT exceed 8% of current equity. This is a hard calculation
  to do before entry, not an estimate — compute it, then size to it.
- Combined stock + options positions count toward the same 8 max open
  positions — this is one book, not two. There is no weekly trade cap.

### Entry timing relative to a catalyst (IV crush awareness)
Added 2026-07-28 after a live lesson: the SLB $52 call (bought right after
a confirmed earnings beat) lost -35.76% of its value over two trading days
while the underlying stock barely moved (-0.3%). The directional read was
never wrong — the stock didn't drop — but the option still bled value
because implied volatility was elevated right after the catalyst and
collapsed afterward (classic post-event IV crush), and this was a
near-the-money call (delta ~0.42), which makes it especially IV-sensitive.
- Buying an option in the minutes/hours immediately after a catalyst
  (earnings beat/miss, major news) means paying an IV premium that is
  likely to deflate over the following days regardless of whether the
  directional thesis proves correct. This is a real, structural cost, not
  a risk that shows up in the Rule 3 max-loss calc.
- Where practical, prefer confirming the move holds for a bit (even
  same-day, later in the session) before entering, rather than chasing
  the very first print after news breaks — or size smaller / prefer
  further-OTM (cheaper, less delta/IV-sensitive) strikes when entering
  immediately is still the better call.
- This is a judgment-call guideline, not a hard rule with a fixed waiting
  period — the goal is awareness that "the stock hasn't moved against me"
  does not mean "the option isn't losing value," especially in the first
  1-3 days after a catalyst.

### Days-to-expiration (DTE) rules
- Do not open a new options position with fewer than 7 DTE (avoid
  gamma/pin risk close to expiration) — this floor stays in place even
  under the aggressive posture above; it's a guardrail against pure
  gambling, not a pacing lever.
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
- The Rule 3 max-loss-at-8%-of-equity calculation, shown explicitly
- If undefined-risk: confirm `options_buying_power` covers Alpaca's
  requirement before attempting the order

## Entry Checklist (stocks)
- Specific catalyst?
- Sector in momentum (or a volatility/event trigger being evaluated per
  Core Rule 9)?
- Stop level (7-10% below entry)
- Target (min 2:1 R:R)
- The Rule 3 max-loss-at-8%-of-equity calculation, shown explicitly
