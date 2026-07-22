# Research Log

Daily pre-market research entries will be appended here. Format each entry:

## YYYY-MM-DD — Pre-market Research

### Account
- Equity: $X
- Cash: $X
- Buying power: $X
- Daytrade count: N

### Market Context
- WTI / Brent:
- S&P 500 futures:
- VIX:
- Today's catalysts:
- Earnings before open:
- Economic calendar:
- Sector momentum:

### Trade Ideas
1. TICKER — catalyst, entry $X, stop $X, target $X, R:R X:1
2. ...

### Risk Factors
- ...

### Decision
TRADE or HOLD (default HOLD if no edge)

## 2026-07-20 — Pre-market Research

### Account
- **UNAVAILABLE — infrastructure blocker.** This session's egress policy returns
  403 (policy denial) on CONNECT to `paper-api.alpaca.markets`,
  `data.alpaca.markets`, `api.perplexity.ai`, and `api.clickup.com` — only
  `github.com`/`api.github.com` is reachable. Confirmed via
  `curl $HTTPS_PROXY/__agentproxy/status` (recentRelayFailures: connect_rejected,
  gateway 403 on CONNECT to paper-api.alpaca.markets:443) and direct curls to
  the other three hosts (all `CONNECT tunnel failed, response 403`). Per the
  proxy's own guidance this is an org policy denial, not a transient fault —
  not retried or routed around. Equity/cash/buying power/daytrade count could
  not be pulled this run. `PERPLEXITY_API_KEY`, `CLICKUP_API_KEY`,
  `CLICKUP_WORKSPACE_ID`, `CLICKUP_CHANNEL_ID` are also unset in this
  environment (separately from the network block).

### Market Context (via WebSearch fallback, Perplexity unreachable)
- WTI: ~$79.77/bbl (Aug '26 contract), up ~0.5% — crude firm on renewed
  US-Iran hostilities and a Houthi "maritime embargo" threat against Saudi
  Arabia near the Strait of Hormuz.
- S&P 500 futures: ES (Sep) ~+0.3% premarket; Nasdaq (NQ Sep) ~+0.6% on a
  mild chip-sector rebound (~+9.9% off recent declines).
- VIX: ~18.8 (futures), range 18.63–19.03 — elevated-but-not-panicked.
- Today's catalysts: US airstrikes on Iran + reports of another US service
  member death; conflicting reports Iran may be open to resuming talks via
  mediators. Big Tech earnings week ahead (Tesla, Alphabet report soon).
  Alibaba previewed a new "Qwen 3.8 Max" AI model, intensifying AI-model
  competition headlines.
- Earnings before open: none major flagged for today specifically; earnings
  season ramps this week (Tesla/Alphabet among the highlights).
- Economic calendar: no CPI/PPI/FOMC/jobs print pinpointed for today in
  search results; broader macro focus this week is on inflation data trending
  and Fed commentary — could not confirm exact day/time of any print (see
  risk factors).
- Sector momentum: 2026 YTD rotation OUT of tech (worst YTD sector recently)
  and INTO Energy (+22%+ YTD, Iran/Strait-of-Hormuz tailwind), Industrials,
  and Consumer Defensive. Tech still leads on some longer YTD windows (+34%)
  but recent leadership has flipped to energy/industrials — sector signal is
  mixed/transitioning, not clean momentum.

### Trade Ideas
None generated this run — account state (equity, cash, buying power,
existing positions, daytrade count) is required by the strategy's entry
checklist and sizing rules and is currently unverifiable due to the Alpaca
API block above. Sizing or entering trades blind, without confirming current
exposure and buying power, would violate Core Rules #2/#3 (75-85% deployed,
max 20% each) and is not attempted.

### Risk Factors
- **Primary/actionable risk today: this environment cannot reach Alpaca,
  Perplexity, or ClickUp.** If unresolved, the bot cannot check positions,
  size or place orders, manage stops, or send trade alerts on future runs
  either — this is a standing blocker, not just a today issue.
- Geopolitical: active US-Iran military exchange + Strait of Hormuz shipping
  threat — elevated oil-price and market-volatility tail risk in either
  direction depending on de-escalation headlines.
- Earnings-week volatility risk building (Tesla/Alphabet) even though not
  today's prints.
- Sector leadership is actively rotating (tech → energy/industrials), which
  raises whipsaw risk for momentum-based entries either way.
- Economic calendar for today could not be fully confirmed — some risk of an
  unflagged data print moving markets intraday.

### Decision
**HOLD.** No trade this run — not a market-conditions call but a hard
capability gate: account/position state cannot be verified, so no entry can
be sized or risk-managed per the strategy's own rules. Flagging the API/
egress blocker for follow-up; it needs to be resolved (session network
policy allowlist for `paper-api.alpaca.markets`, `data.alpaca.markets`,
`api.perplexity.ai`, `api.clickup.com`, and setting the four missing env
vars) before this bot can trade or alert normally.

## 2026-07-20 20:24 UTC — Pre-market Research (re-run)

### Infra note
- Alpaca now reachable (unlike the earlier run above) — account/positions/
  orders pulled successfully this run.
- `PERPLEXITY_API_KEY` still unset -> `scripts/perplexity.sh` exited 3 as
  designed; fell back to native WebSearch for all queries below.
- `CLICKUP_API_KEY`/`CLICKUP_WORKSPACE_ID`/`CLICKUP_CHANNEL_ID` still unset
  -> `scripts/clickup.sh` will use its local `DAILY-SUMMARY.md` fallback
  instead of posting to ClickUp Chat.

### Account
- Equity: $100,000 | Cash: $100,000 | Buying power: $400,000
- Positions: none | Open orders: none | Daytrade count: 0
- Day 0 — bot has not entered a position yet.

### Market Context (WebSearch fallback)
- Oil: WTI ~$82.21/bbl (-0.34%), Brent ~$87.72/bbl (-0.44%); briefly topped
  $90 Brent over the weekend on US-Iran strikes before easing on renewed
  diplomatic-talk headlines.
- S&P 500 futures: mixed/modestly higher (~+0.13% ES), Nasdaq futures
  supported by a chip-sector bounce; conflicting reports of session direction
  — sentiment fragile, headline-driven.
- VIX: ~17.2 (range 16.15–17.56 today), down from Friday's ~18-19 spike but
  still elevated vs. typical calm-market sub-15 levels.
- Catalysts: fresh US airstrikes on Iran + another US service-member death;
  Yemeni forces declared a "maritime embargo" on Saudi Arabia; chip stocks
  recovering ahead of Big Tech earnings (Tesla, Alphabet, Intel, IBM) later
  this week.
- Earnings before open: none major confirmed for today specifically;
  AGNC and others report after close today; earnings season accelerates
  Tue-Thu (73/134/169 companies).
- Economic calendar: no CPI/PPI/jobs print confirmed for today; FOMC meets
  July 28-29 (not this week). No major scheduled data release found for
  today — low macro-print risk, high geopolitical-headline risk.
- Sector momentum: Energy (+22% YTD) and Healthcare (flight-to-safety) are
  YTD leaders; broader rally still highly concentrated in ~10 mega-cap
  AI/tech names (~78% of S&P YTD return through mid-May) — narrow breadth,
  fragile leadership.

### Trade Ideas
1. Energy sector (e.g. XLE or large-cap E&P) — catalyst: Strait of
  Hormuz/Iran supply-risk premium — flagged as a watchlist idea only;
  no entry sized today given only Day 0 and 0 verified R:R setups pulled.
2. Semis/chip bounce (post-selloff) — catalyst: pre-earnings positioning
  ahead of Tesla/Alphabet/Intel — high headline-reversal risk, not
  actionable without clearer confirmation.

### Risk Factors
- Headline-driven, two-way volatility from the active US-Iran conflict —
  both oil and equities can gap sharply on de-escalation or escalation news
  intraday.
- Market breadth is narrow (concentrated AI/mega-cap leadership) — chasing
  the tape here has elevated whipsaw risk.
- Big Tech earnings (Tesla, Alphabet, Intel, IBM) this week — pre-earnings
  positioning is speculative; better to wait for prints.
- ClickUp/Perplexity creds still missing — alerting and primary research
  path degraded; flagging for follow-up (not blocking today's HOLD).

### Decision
**HOLD.** Day 0, no verified edge with sufficient R:R; geopolitical
headline risk argues for patience. Will revisit energy/semis watchlist
ideas once a clean setup with defined entry/stop/target confirms.

## 2026-07-20 21:15 UTC — Pre-market Research (2nd re-run today)

### Infra note
- Alpaca reachable; account/positions/orders pulled successfully.
- `PERPLEXITY_API_KEY` still unset -> `scripts/perplexity.sh` exited 3 as
  designed; fell back to native WebSearch for all queries below.
- `CLICKUP_API_KEY`/`CLICKUP_WORKSPACE_ID`/`CLICKUP_CHANNEL_ID` still unset
  -> `scripts/clickup.sh` will use its local `DAILY-SUMMARY.md` fallback.
- This run landed only ~51 min after the prior 20:24 UTC entry (both
  labeled "pre-market" despite firing well after the US cash open at
  13:30 UTC) — market context below is materially unchanged from that
  entry; treat this as a confirmation pass, not new information.

### Account
- Equity: $100,000 | Cash: $100,000 | Buying power: $400,000 |
  Options buying power: $100,000
- Positions: none | Open orders: none | Daytrade count: 0
- Still Day 0 — no trade has been entered yet.

### Market Context (WebSearch fallback)
- Oil: WTI ~$82.21/bbl (-0.34%), Brent ~$87.72/bbl (-0.44%) — unchanged
  from the last run; still elevated on Iran-conflict supply risk.
- S&P 500 futures/session: premarket showed +0.13% (SPY +0.44% premarket,
  68% odds of an "up" open per one prediction-market source), but same-day
  summaries also show the cash session closing lower — S&P 500 -0.19% to
  7,443.40, Dow -0.59%, Nasdaq -0.05%. Search results are blending
  premarket and full-day data for the same date; treat as noisy/
  headline-driven rather than a clean directional read.
- VIX: opened ~17.2, trading in the 17-18 range — elevated vs. calm-market
  sub-15 but off Friday's ~18-19 spike.
- Catalysts: US-Iran conflict still escalating — 9th straight day of US
  strikes, Iran retaliated by bombing Kuwait, Houthi forces declared a
  "maritime embargo" on Saudi oil exports; a mediator-proposed 10-day
  ceasefire has not been accepted by both sides. Trump said Iran "will
  pay" for US casualties. Chip stocks bouncing on peace-talk hope headlines
  even as the broader conflict continues.
- Earnings: ~40 companies report today (incl. STLD, RYAAY) but no major
  premarket-specific names confirmed; real earnings-season catalyst is
  Tesla/Alphabet/ServiceNow/IBM/Intel/Texas Instruments/AT&T/Verizon/
  T-Mobile/Comcast later this week, not today.
- Economic calendar: no CPI/PPI/jobs print confirmed for today; FOMC not
  until July 28-29 — low scheduled-macro risk, high geopolitical-headline
  risk, same as last run.
- Sector momentum: mixed/conflicting signals — Energy still +22% YTD in
  one source but another flags large-cap energy names down 13% recently;
  Healthcare holding up as a flight-to-safety trade. Broader takeaway
  unchanged: leadership is extremely narrow (~10 mega-cap AI names ≈78%
  of S&P YTD return through mid-May), so momentum entries carry elevated
  whipsaw/reversal risk either direction.

### Trade Ideas
1. Energy (e.g. XLE) — catalyst: Strait of Hormuz/Iran supply-risk premium
   keeping oil bid. Framework only (no live quote pulled): entry near
   market, stop 7-10% below entry per Core Rule #3, target sized for
   >=2:1 R:R. Watchlist only — conflicting momentum signals (some sources
   show energy large-caps down double digits recently) argue against
   sizing today.
2. Semis/chip bounce (SOXX or single names) — catalyst: pre-earnings
   positioning ahead of this week's Big Tech prints (Tesla, Alphabet,
   Intel). High headline-reversal risk given ongoing Iran conflict; not
   actionable without a confirmed technical setup.
3. No options idea today — Day 0, zero existing exposure, and the two
   equity ideas above are unconfirmed watchlist items, not qualified
   entries; adding options exposure before a stock-side setup is validated
   would be premature per Core Rule #10 (patience > activity).

### Risk Factors
- Active, escalating US-Iran conflict (9 days of strikes, Kuwait bombed,
  Saudi oil "embargo" threat) — two-way gap risk on any
  escalation/de-escalation headline.
- Search data for "today" is internally inconsistent (premarket-gain
  reports vs. same-day-close-lower reports) — a sign the underlying
  sources are noisy/stale for same-day queries; do not treat any single
  figure above as precise.
- Narrow market breadth (mega-cap AI concentration) raises whipsaw risk
  for any momentum-chasing entry.
- Big Tech earnings week (Tesla, Alphabet, IBM, Intel, TXN) — pre-earnings
  positioning is speculative; better to wait for confirmed prints.
- ClickUp/Perplexity creds still missing — degrades alerting and primary
  research path; not a blocker for today's HOLD but a standing infra gap.

### Decision
**HOLD.** No material change from the 20:24 UTC entry — still Day 0, still
no verified R:R>=2:1 setup, still elevated geopolitical/headline risk.
Watchlist ideas (energy, semis) carry forward; will act only once a clean
technical setup with defined entry/stop/target confirms.

## 2026-07-21 22:49 UTC — Pre-market Research (3rd re-run, effectively post-close)

### Infra note
- Alpaca reachable; account/positions/orders pulled successfully.
- `PERPLEXITY_API_KEY` still unset -> `scripts/perplexity.sh` exited 3 as
  designed; fell back to native WebSearch for all queries below.
- `CLICKUP_API_KEY`/`CLICKUP_WORKSPACE_ID`/`CLICKUP_CHANNEL_ID` still unset
  -> `scripts/clickup.sh` will use its local `DAILY-SUMMARY.md` fallback.
- This run fired at 22:49 UTC — well after the US cash close (20:00 UTC).
  WebSearch results for "today" are full-day recaps of the completed July 21
  session, not premarket data. Treating this as an EOD/overnight-prep
  entry rather than a true premarket read; tomorrow's premarket levels will
  differ from what's captured here.

### Account
- Equity: $100,000 | Cash: $100,000 | Buying power: $400,000 | Options
  buying power: $100,000
- Positions: none | Open orders: none | Daytrade count: 0
- Still Day 0/flat — no trade has been entered yet across three research
  cycles today.

### Market Context (WebSearch fallback, EOD recap for Jul 21)
- Oil: WTI ~$83-84/bbl, Brent slipped below $89/bbl after surging ~6% over
  the prior two sessions on US-Iran escalation (10th straight day of US
  strikes; Iran hit Kuwait with missiles/drones); still up ~2% intraday
  before easing on ceasefire-talk headlines.
- Indices (close): S&P 500 +0.89% to 7,509; Nasdaq +1.29% to 25,837; Dow
  +0.74% to 52,225 — snapped a three-session losing streak. Rally led by
  memory-chip names (Micron +12%, SanDisk +14%) plus Nvidia commentary on
  new chip designs shipping to customers.
- VIX: ~17.05, roughly unchanged on the session — mid-band (12-20), calmer
  than Friday's spike but still above typical sub-15 calm-market levels.
- Catalysts: semiconductor/memory-chip strength offsetting geopolitical and
  tariff risk; USTR Greer hinted new tariffs against several countries may
  be coming; earnings beats from 3M and GM helped sentiment.
- Earnings before open (Jul 21): 3M, Alaska Air, Annaly Capital, Capital
  One, Danaher, GM, Halliburton, Northrop Grumman, Novartis, Charles
  Schwab — GM beat Q2 estimates. Bigger tech prints (Tesla, IBM, Alphabet)
  still upcoming later this week.
- Economic calendar: today was FOMC-speaker-only (Bullard); CPI prints
  tomorrow (Wed) 8:30am, PPI + jobless claims Thursday 8:30am, FOMC meeting
  not until Jul 28-29. Next 48h carries real macro-print risk (CPI/PPI).
- Sector momentum: Materials leading YTD (+22%), with Industrials, Staples,
  Energy also showing relative strength; Healthcare holding up as
  flight-to-safety. Tech, Communications, Discretionary, Financials lagging
  on a sector-momentum basis even though today's session was led by
  semis/memory names specifically — a divergence between today's single-day
  leadership and multi-week sector momentum, worth flagging as noise vs.
  trend.
- No held positions, so no held-ticker news check applicable (account flat).

### Trade Ideas
1. Memory/semis bounce (e.g. MU, SNDK, or SOXX) — catalyst: today's
   12-14% single-day surges on AI-demand/chip-design news. NOT actionable
   as a chase-the-pop entry; day-after-12%+ moves have poor risk-adjusted
   entry R:R and this run is already past close. Watchlist only: would
   need a pullback/consolidation entry with defined stop (7-10% below
   entry per Core Rule #3) and >=2:1 target before sizing.
2. Materials sector momentum (e.g. XLB) — catalyst: +22% YTD leadership,
   multi-week trend rather than single-day noise. Framework only (no live
   intraday quote pulled this run): entry near market on next session open,
   stop 7-10% below entry, target sized for >=2:1 R:R. Needs a fresh
   technical check next session before sizing.
3. No options idea today — flat account, two equity ideas above are still
   unconfirmed watchlist items; CPI print tomorrow argues for waiting
   through that catalyst before adding gamma-sensitive short-DTE exposure
   per Core Rule #10 (patience > activity).

### Risk Factors
- CPI (tomorrow) and PPI/jobless claims (Thursday) are live macro catalysts
  this week — elevated event risk for any position opened today.
- Active US-Iran conflict (10 days of strikes, Kuwait hit) — continued
  two-way gap risk in oil and broader risk sentiment on escalation/
  de-escalation headlines.
- Today's rally was narrow (memory/semis-led) — chasing it after the move
  has weak R:R; divergence vs. broader sector-momentum leaders (Materials,
  Industrials) worth watching for confirmation or reversal.
- Big Tech earnings (Tesla, IBM, Alphabet) still ahead this week — another
  source of post-close gap risk for anything correlated to mega-cap tech.
- Run timing: this "premarket" cycle fired post-close (22:49 UTC); data
  reflects completed session, not tomorrow's open — flagging for possible
  schedule review, not a blocker for today's HOLD.
- ClickUp/Perplexity creds still missing — degrades alerting and primary
  research path; standing infra gap, not a blocker for today's HOLD.

### Decision
**HOLD.** Three research cycles today, still zero verified R:R>=2:1 setup
with a live executable quote. Today's chip-driven rally is a chase risk,
not a confirmed entry; CPI print tomorrow argues for patience before
opening gamma-sensitive or leveraged exposure. Will revisit Materials
sector-momentum and semis-pullback ideas next session with fresh quotes.

## 2026-07-22 07:36 UTC — Pre-market Research

### Infra note
- Alpaca reachable; account/positions/orders pulled successfully.
- `PERPLEXITY_API_KEY` still unset -> `scripts/perplexity.sh` exited 3 as
  designed; fell back to native WebSearch for all queries below.
- `CLICKUP_API_KEY`/`CLICKUP_WORKSPACE_ID`/`CLICKUP_CHANNEL_ID` still unset
  -> `scripts/clickup.sh` will use its local `DAILY-SUMMARY.md` fallback.
  Standing infra gap across every run so far; not a blocker.

### Account
- Equity: $100,000 | Cash: $100,000 | Buying power: $100,000 | Options
  buying power: $100,000
- Positions: none | Open orders: none | Daytrade count: 0
- Still Day 0/flat — no trade has been entered yet across four research
  cycles now.

### Market Context (WebSearch fallback)
- Oil: WTI ~$84.29/bbl (+2.2% Jul 21), Brent ~$91.10-91.33/bbl (+2.1%),
  climbing further on pessimism over US-Iran peace talks — another tanker
  reportedly struck near the Strait of Hormuz and Houthi militants
  threatening to block Saudi maritime traffic in the Red Sea. Two-way
  headline-gap risk remains live and is intensifying, not fading.
- Indices: S&P 500 futures trading ~7,514-7,554 (vs. Tue close 7,509),
  modestly firmer premarket. Tuesday's cash session: S&P +0.89% to 7,509,
  Nasdaq +1.29%, Dow +0.74%, led by chip/AI names; Asian markets extended
  the rally overnight (MSCI APAC +1.3%, Kospi +4.6% on unwind of leveraged
  shorts).
- VIX: closed 18.65 Jul 21, up from ~17.05 the prior read — elevated and
  rising into a CPI print, not the calm backdrop the last research cycle
  described.
- Catalysts: chip/AI rally still running; oil bid on Iran-conflict
  pessimism; markets await Alphabet and Tesla earnings today (Jul 22),
  with Meta/Microsoft/Amazon/Apple following next week.
- Earnings before open today: IBM, Texas Instruments, ServiceNow, AT&T,
  GE Vernova, Otis, Northern Trust, CME Group, Moody's, PulteGroup, and
  others. Alphabet and Tesla report after today's close — major event risk
  for anything correlated to mega-cap tech/AI into the print.
- Economic calendar: **CPI today at 8:30am ET** — the key macro print of
  the week, released before/at the open. PPI + jobless claims tomorrow
  (Thu) 8:30am. FOMC meeting not until Jul 28-29; Fed speakers this week
  include Kashkari (Wed) and Waller (Thu).
- Sector momentum: conflicting reads across sources this cycle — prior
  entries had Materials/Industrials/Energy/Staples leading YTD with
  Healthcare as flight-to-safety; today's search also surfaced an Energy
  +22%-YTD claim alongside a note that Energy has since lagged (large caps
  -13%) by June, i.e. stale/contradictory YTD figures depending on the
  source's as-of date. Treating sector-momentum leadership as unconfirmed
  this cycle rather than acting on it — needs a single clean as-of-today
  source before using it to pick a trade.
- No held positions, so no held-ticker news check applicable (account
  still flat).

### Trade Ideas
1. Semis/AI continuation (e.g. SOXX, or a name that already digested
   Tuesday's chip pop rather than chasing it) — catalyst: multi-day AI/chip
   rally plus favorable overnight Asia read. NOT actionable pre-CPI: entry
   before the 8:30am print risks a stop-out on a print-driven gap in
   either direction. Watchlist only — would need a post-CPI, post-reaction
   technical setup with 7-10% stop and >=2:1 target before sizing.
2. Energy/oil-linked names (e.g. XLE, or majors) — catalyst: WTI/Brent up
   another leg on Iran-conflict escalation (second tanker strike, Houthi
   shipping threat). Two-way risk is high (any ceasefire headline reverses
   the move fast), so this is a watch-only idea pending a defined technical
   level, not a same-day entry.
3. No options idea today — today stacks a major macro print (CPI at the
   open) directly against megacap earnings after the close (Alphabet,
   Tesla). Per Core Rule #10 (patience > activity) and the options DTE/
   entry-checklist rules, opening gamma-sensitive short-DTE exposure into
   this specific combination of catalysts is exactly the setup those rules
   exist to avoid. Skip for today; revisit once CPI and the earnings prints
   have cleared.

### Risk Factors
- CPI print today at the open is the single largest near-term catalyst —
  elevated event risk for any position opened before or shortly after
  8:30am ET.
- Alphabet and Tesla report after today's close — gap risk into tomorrow
  for anything correlated to mega-cap tech/AI, on top of CPI.
- Active, apparently escalating US-Iran conflict (second tanker strike,
  Houthi threat against Saudi shipping) — VIX rising to 18.65 alongside it;
  continued two-way gap risk in oil and broader risk sentiment.
- Sector-momentum data was contradictory across sources this cycle (see
  Market Context) — do not size a trade off sector leadership until a
  single reliable as-of-today source confirms it.
- Four consecutive research cycles now with zero trades — worth a
  deliberate check next cycle on whether the entry bar is calibrated
  correctly (per TRADING-STRATEGY.md's guidance to flag a repeatedly-
  failing rule/parameter), or whether market conditions (headline-driven,
  event-stacked) have simply not offered a qualifying setup yet. Current
  read: conditions, not calibration — today alone stacks CPI + megacap
  earnings, a legitimate reason to wait.
- ClickUp/Perplexity creds still missing — degrades alerting and primary
  research path; standing infra gap, not a blocker for today's HOLD.

### Decision
**HOLD.** CPI print at the open plus Alphabet/Tesla earnings after close
stack two major catalysts into one session — textbook patience-over-
activity conditions per Core Rule #10. No verified R:R>=2:1 setup with a
live executable quote and a stable technical picture. Will revisit
semis-continuation and energy/oil-linked ideas once CPI and today's
earnings have cleared and sector-momentum data can be confirmed from a
single consistent source.
