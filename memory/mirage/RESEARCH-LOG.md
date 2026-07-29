# Mirage Research Log

Same-day, dated entries appended here each trading day. Format each entry:

## YYYY-MM-DD HH:MM UTC — Morning Entry Research

### Account
- Equity: $X
- Cash: $X
- Buying power: $X
- Options buying power: $X

### Today's Specific Catalysts
- Gaps at the open (ticker, % gap, why, holding or fading)
- Earnings reactions today (ticker, beat/miss, live price confirmation)
- Unusual volume/news items dated today
- Relevant economic data released this morning

### Trade Ideas
1. TICKER — same-day catalyst, entry $X, stop $X (2-3%), target $X,
   R:R X:1, Rule 1 max-loss calc shown
2. ...

### Risk Factors
- ...

### Decision
TRADE or HOLD (HOLD only if nothing same-day-specific clears the bar)

## 2026-07-27 13:20 UTC — Morning Entry Research

### Account
- Equity: $50,000
- Cash: $50,000
- Buying power: $200,000
- Options buying power: $50,000
- Positions: none | Open orders: none (fresh account, Day 1 of live trading)

### Today's Specific Catalysts
- Pre-market gappers: no reliable live premarket data available via WebSearch
  today — results returned generic listing pages and stale data from
  ~July 21-22, not today's session (e.g. a "WBUY +39.8%" hit was dated
  days earlier, not July 27). No verifiable same-day gapper with a stated
  reason could be confirmed.
- Earnings before today's open: none confirmed. WELL and CDNS both showed
  up on generic Monday earnings-calendar listings, but direct checks show
  WELL reports *after* today's close (call is tomorrow 7/28 9am ET) and
  CDNS reports *after* today's close (5pm ET today). Neither is a
  before-open reaction to trade this morning.
- Unusual volume/news dated today: none found. No FDA approvals, contract
  wins, or analyst upgrade/downgrade items dated specifically 2026-07-27
  turned up in search.
- Economic data: none scheduled today. This week's calendar is light —
  jobless claims Thursday, new home sales Friday, FOMC decision
  Wednesday 7/29. Nothing releases today.

### Trade Ideas
None. No idea reached the research stage — there is no same-day catalyst
to build a Rule 1 calc around, so no ticker/entry/stop/target proposed.

### Risk Factors
- WebSearch cannot reliably surface live pre-market tape (gappers, RVOL)
  for the current session — it's not a real-time data source, so absence
  of evidence here is a data-access limitation, not proof nothing is
  moving. Live quotes were not pulled for any speculative ticker since no
  candidate cleared even the first screen (a stated, dated reason).
  Note for a future iteration: cross-check Alpaca's own market-data quote
  endpoint against a short watchlist even on quiet mornings, rather than
  relying on WebSearch alone for gapper discovery.
- Two-day-out FOMC decision (Wed 7/29) may keep index-level volatility
  compressed today as the market waits — lower odds of a clean same-day
  breakout setup materializing later in the session too.

### Decision
HOLD — no same-day-specific catalyst clears the entry checklist. No
stock or option positions opened this morning. Will re-check at midday
for anything that develops intraday.

## 2026-07-27 (midday check)

### Positions & Orders
- Open positions: none | Open orders: none (consistent with morning
  HOLD — nothing to manage, no exits to make).

### New Catalyst Screen
- Re-swept for anything genuinely new since the morning check. Findings
  were broad earnings-season commentary (S&P 500 beat-rate stats,
  Alphabet's post-earnings slide pressuring megacaps, Booz Allen Hamilton
  up on an EPS beat) — none of it a specific, dated-today, tradeable
  setup with a live quote to build a Rule 1 calc around. Amazon/Meta/
  Microsoft report Wed/Thu, not today. No FDA approvals, contract wins,
  or same-day gap-and-hold setups surfaced.
- Same WebSearch limitation noted this morning applies: no reliable
  live intraday tape (gappers, RVOL) for the current session.

### Decision
HOLD — no genuinely new same-day catalyst clears the bar. No new
position opened. Nothing open to manage. Next check-in: mandatory EOD
close.

## 2026-07-27 (evening research — watchlist for tomorrow)

### Account (sanity check)
- Confirmed flat: yes, equity $50,000, 0 positions, 0 open orders (EOD-close ran as expected)

### Tomorrow's Setups to Watch
- CDNS (Cadence Design Systems) — reported Q2 after today's close; consensus was EPS $2.05 / rev $1.58B against a prior FY26 guide raise to ~$6.2B rev. Reaction still developing at time of writing (WebSearch can't see the print/after-hours tape). Confirm at open: gap direction vs. consensus, and whether it holds above/below prior close — software/semis-design names have been reaction-sensitive this earnings season.
- XOM, CVX (energy majors) — both report before tomorrow's open. Watch for a coordinated sector gap; confirm with early volume in XLE if fading or holding.
- ABBV, MRNA (pharma/biotech) — both report before tomorrow's open; watch for guidance-driven gaps, confirm with first-15-min range before committing.
- Broader macro backdrop: Alphabet fell 7.1% last Thursday on capex/free-cash-flow concerns (its worst earnings reaction since Feb 2025), reinforcing a "AI spenders punished / semis rewarded" dynamic. MSFT, META, ARM report Wednesday after close and AAPL/AMZN Thursday after close (not tomorrow), but expect continued positioning/rotation chatter tomorrow that could move megacap tech and semis even without a same-day print.

### Notes
- Econ calendar tomorrow is light: Consumer Confidence (10:00 ET), Richmond Fed Manufacturing (10:00 ET), Dallas Fed Texas Retail Outlook (10:30 ET) — none are typically index-moving; Consumer Confidence is the only one worth a glance if it's a big beat/miss. No CPI/GDP/FOMC tomorrow (GDP advance estimate + PCE land Thursday 7/30).
- No unusual after-hours mover of tradeable size/quality surfaced via WebSearch tonight — after-hours screens were dominated by illiquid micro-caps, not actionable.
- Overall: earnings-heavy morning (energy + pharma + CDNS reaction) gives a few gap-and-go candidates to confirm live at the open; nothing here should be treated as a pre-committed trade — all setups require intraday tape confirmation before entry.

## 2026-07-27 21:07 UTC (evening research — watchlist for tomorrow)

### Account (sanity check)
- Confirmed flat: yes, equity $49,056.48, 0 positions (bash scripts/alpaca.sh positions returned [])

### Tomorrow's Setups to Watch
- INTC (Intel) — reported Q2 after today's close: EPS $0.42 vs. $0.21 consensus, revenue $16.13B vs. $14.33B consensus, both big beats. Stock fell 2.46% into the close, then swung to +3.44% after hours on AI-demand/margin commentary — a genuinely two-sided, still-unsettled reaction. Overhang: FY26 capex guide raised to $20B+ (~$3B above prior plan), which is the bear case. Confirm at open: gap direction, whether it holds above/below today's $100.10 close in the first 15 min before treating as a momentum long or fade.
- FOMC meeting begins tomorrow (July 28) with the rate decision landing Wednesday July 29 at 2:00pm ET — no decision tomorrow, but a "quiet before the print" dynamic can suppress follow-through on other setups. Econ data tomorrow: Consumer Confidence, Richmond Fed Mfg (both 10:00 ET), Dallas Fed Texas Retail Outlook (10:30 ET) — none typically index-moving; Consumer Confidence is the only one worth a glance on a big beat/miss.
- Before-open earnings tomorrow: UPS, Boeing (BA), Coca-Cola (KO), PayPal (PYPL), Corning (GLW), Hilton (HLT), Royal Caribbean (RCL), Ecolab (ECL), Oshkosh (OSK). Boeing and UPS are the two with the most history of outsized gap-and-hold moves; confirm live at open before sizing anything.
- Semis broadly weak today (AMD -5%, Teradyne -4%, Micron -2%) ahead of a heavy megacap-tech earnings week (MSFT/META/ARM Wed after close, AAPL/AMZN Thu after close — not tomorrow). Watch whether INTC's beat provides sector support or gets overwhelmed by continued AI-capex-fatigue rotation out of chips tomorrow morning.
- Crypto-proxy stocks (Bitmine, Strategy, Coinbase) rallied today on the US/Iran strike pause; oil fell on the same news. Not a tomorrow-specific catalyst by itself, but worth noting as context if oil/crypto continue trending on the truce holding or breaking overnight.

### Notes
- No single overwhelming catalyst for tomorrow — it's a "confirm at the open" day: INTC's reaction is unresolved, several mid-cap industrials/consumer names report before the bell, and FOMC day-before positioning could add chop. Normal intraday scan with extra attention on INTC gap direction and the Boeing/UPS/Coca-Cola prints.
- WebSearch limitation stands: can't see live after-hours tape/RVOL, so INTC's actual after-hours settle price and any other stealth after-hours movers need to be confirmed live tomorrow morning, not assumed from tonight's headlines.

## 2026-07-28 21:08 UTC (evening research — watchlist for tomorrow)

### Account (sanity check)
- Confirmed flat: yes, equity $49,038.20, 0 positions (bash scripts/alpaca.sh positions returned [])

### Tomorrow's Setups to Watch
- FOMC rate decision at 2:00pm ET tomorrow (statement + implementation note), press conference 2:30pm ET. Non-SEP meeting, so no updated dot plot/projections. Fed has held 3.50-3.75% through Jan/Mar/Apr/June 2026, citing inflation above target — a hold is the base case, so the tradeable catalyst is Powell's tone in the press conference, not the decision itself. Confirm live: does SPY/QQQ chop into 2pm then break on the statement/presser, watch for a reversal candle either direction.
- MSFT and META both report Q2 tomorrow (7/29) — META confirmed after market close (call 4:30pm ET), MSFT also reporting same day. This means the earnings reaction lands Thursday morning (7/30), not tomorrow's open — but expect elevated positioning/hedging chatter in both names and in semis tomorrow ahead of the print, layered on top of FOMC day. Not a tomorrow-morning gap play by itself; note for Thursday's research instead.
- Memory/chip sector rout continuing: SanDisk (SNDK) closed -14.14% today, down ~35% over three sessions, extending Monday's SK Hynix -7.47% and Tuesday's Micron/AMD >8% drops. Driver: AI-memory-trade unwind + fear of Chinese NAND/DRAM competition (CXMT's ~$487B Shanghai IPO) pressuring margins, plus Fed commentary on stretched tech valuations. Watch SNDK, MU, WDC, SK Hynix-linked names at tomorrow's open for continuation vs. dead-cat bounce; this is a live, still-unresolved trend, not a one-day event.
- Today's session context: Dow +1.03% (chip weakness offset by earnings optimism/falling oil), S&P +0.21%, Nasdaq -0.22%. Sherwin-Williams +8% and Coca-Cola +5% on beats — no incremental catalyst for tomorrow from either, just confirms a "industrials/consumer staples beats, semis punished" rotation that could persist into tomorrow's FOMC session.
- No before-open earnings of size confirmed for tomorrow beyond the MSFT/META after-close pair; will recheck live at open since after-hours WebSearch coverage is incomplete.

### Notes
- Tomorrow is dominated by one macro catalyst (FOMC 2pm ET) layered on an already-jumpy tape (semis/memory unwind). Expect a quiet morning followed by a directional move into/after the 2pm decision and presser — normal intraday scan pre-2pm, heightened attention post-2pm.
- The MSFT/META prints are real but their tradeable reaction is a Thursday story, not tomorrow's — flagged here so it isn't missed, but no tomorrow-morning setup is being built around them.
- WebSearch limitation stands: can't see live after-hours/premarket tape, so tomorrow's actual gappers (especially in the memory/chip complex) need live confirmation at the open, not assumption from tonight's headlines.

## 2026-07-29 (evening research — watchlist for tomorrow)

### Account (sanity check)
- Confirmed flat: yes, equity $47,687.49, 0 positions (bash scripts/alpaca.sh positions returned [])

### Tomorrow's Setups to Watch
- META — reported Q2 after today's close: EPS $6.18 missed the $7.14 consensus; revenue $60.8B beat ($60.2B consensus); ad revenue $59.3B beat. FY26 capex guidance raised to $135-145B (low end up $10B in one quarter). Shares fell ~8% in after-hours on the capex overhang. Confirm at open: gap direction vs. after-hours print, whether it holds below today's close in the first 15 min before treating as a momentum short or fade-the-gap long.
- MSFT — reported Q4 FY26 after today's close: beat on both lines ($4.74 EPS vs. $4.24 consensus; $90.01B rev vs. $87.61B consensus), Azure crossed $100B FY revenue for the first time. Shares rose ~2% after hours — a much calmer reaction than META. Confirm at open whether the +2% holds or fades once combined with broader tech tape.
- AAPL, AMZN — both report tomorrow (7/30) after market close, so their reaction is a Friday story, not tomorrow morning. Note for tomorrow evening's research, not a tomorrow-AM setup.
- Heavy before-open earnings slate tomorrow (7/30): MA, VLO, BMY, CI, RACE, OWL, MO, PWR, STLA, BAX, EPD, SHEL, HSY, NCLH, PBF, REGN, AEP, ICE, IP, MLM, XRX, BUD, and dozens more. No single one flagged as outsized-mover-of-size yet; recheck premarket for gap leaders since this list is too broad to pre-commit to any one name.
- Semis/chip rout — Nasdaq 100 entered technical correction (~10% off June peak) as the chip selloff extended a 4th straight session: Sandisk -14%, AMD/ARM/Micron/Seagate each -8%+, Intel -6%, Western Digital -7%. Driver: reports of a Chinese chipmaking breakthrough plus a deepening memory-chip crisis and a forecast 13% YoY collapse in global smartphone volumes. This is a live, unresolved multi-day trend — watch SNDK/MU/WDC/AMD at tomorrow's open for continuation vs. dead-cat bounce.
- Broader macro backdrop: Fed held rates at 3.50-3.75% today as expected, but 3 members (Hammack, Kashkari, Logan) dissented in favor of a hike — a hawkish-leaning dissent count that, combined with 30-year Treasury yields hitting their highest since 2007 and Brent crude topping $90, drove a broad risk-off day (Dow -2.19%, its worst since April 2025; S&P -1.5%). Expect continued yield/inflation-driven chop tomorrow layered on top of the megacap-earnings and chip-sector reactions.

### Notes
- Tomorrow is a genuinely loaded session: two megacap earnings reactions (META down hard, MSFT up modestly) resolving at the open, a still-unresolved multi-day semis/memory rout, a hawkish-dissent Fed digest, and a very heavy before-open earnings slate on top. Expect an active, gappy morning — confirm every setup with live premarket/first-15-min tape before sizing; nothing here is pre-committed.
- WebSearch limitation stands: can't see live premarket tape, so actual gap sizes/direction for META, MSFT, and the before-open earnings names need live confirmation at the open, not assumption from tonight's headlines.
