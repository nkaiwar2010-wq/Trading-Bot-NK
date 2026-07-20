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
