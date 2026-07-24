# Weekly Review

Friday reviews appended here. Template for each entry:

## Week ending YYYY-MM-DD

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio | $X |
| Ending portfolio | $X |
| Week return | ±$X (±X%) |
| S&P 500 week | ±X% |
| Bot vs S&P | ±X% |
| Trades | N (W:X / L:Y / open:Z) |
| Win rate | X% |
| Best trade | SYM +X% |
| Worst trade | SYM -X% |
| Profit factor | X.XX |

### Closed Trades
| Ticker | Entry | Exit | P&L | Notes |

### Open Positions at Week End
| Ticker | Entry | Close | Unrealized | Stop |

### What Worked
- ...

### What Didn't Work
- ...

### Key Lessons
- ...

### Adjustments for Next Week
- ...

### Overall Grade: X

## Week ending 2026-07-24

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio (Mon AM, Jul 20) | $100,000.00 |
| Ending portfolio (Fri, live pull) | $99,981.00 |
| Week return | -$19.00 (-0.02%) |
| S&P 500 week | -0.42% (7,443.28 -> 7,411.98) |
| Bot vs S&P | +0.40 pp (outperformed) |
| Trades | 5 (W:0 / L:0 / open:5) — zero closed trades this week |
| Win rate | N/A — no closed trades yet |
| Best position (unrealized) | SLB260821C00052000 +32.7% |
| Worst position (unrealized) | XLE260821C00061000 -21.7% |
| Profit factor | N/A — no closed trades |

**Challenge pace:** Day 6 of 30, 26 days remaining to 2026-08-19. Equity
$99,981 vs. $150,000 target = -$19 of the $50,000 goal (-0.04%). Time
elapsed ~20% (6/30 days) vs. ~0% of target achieved -> **behind linear
pace** (a perfectly on-pace week 1 would show ~+$10,000). Not a pace
emergency yet (per TRADING-STRATEGY.md, escalation only triggers once
"behind pace + deadline approaching," and 26 days/87% of runway remain),
but the gap is real: hitting $150,000 from here requires ~$1,924/day or
~$13,470/week average profit over the remaining 26 days (~13.5%/week on
current equity) — a materially higher bar than this week's ~flat result.
Bias-toward-action (Core Rule 11) argues for more deployed capital and
more distinct catalysts next week, not slowing down.

### Trades This Week (all still open — stocks + options combined book)
| Ticker/OCC | Type | Entry | Current | Qty | Unrealized P&L | Notes |
|---|---|---|---|---|---|---|
| XLE | Stock | $59.21 | $59.67 | 506 sh | +$230.43 (+0.77%) | Energy/oil-supply-shock thesis; 10% trailing stop active |
| XLE260821C00058500 | Long call | $2.33 | $2.52 | 10 | +$190.00 (+8.15%) | Same XLE thesis, defined-risk sleeve |
| XOP | Stock | $178.98 | $174.14 | 169 sh | -$817.96 (-2.70%) | E&P-weighted energy diversifier; well inside 10% stop |
| XLE260821C00061000 | Long call | $1.61 | $1.26 | 20 | -$700.00 (-21.74%) | Roughly halfway to -50% stop-close trigger — watch first Monday |
| SLB260821C00052000 | Long call | $1.65 | $2.19 | 20 | +$1,080.00 (+32.73%) | Idiosyncratic post-earnings-beat catalyst, distinct from pure oil-price beta |

### Open Positions at Week End
| Ticker/OCC | Entry | Current | Unrealized | DTE (to 2026-08-21) | Stop/Close Plan |
|---|---|---|---|---|---|
| XLE | $59.21 | $59.67 | +$230.43 | n/a (stock) | 10% trailing stop GTC |
| XLE260821C00058500 | $2.33 | $2.52 | +$190.00 | 28 | Close at -50% or +50-100% gain |
| XOP | $178.98 | $174.14 | -$817.96 | n/a (stock) | 10% trailing stop GTC |
| XLE260821C00061000 | $1.61 | $1.26 | -$700.00 | 28 | Close at -50% (~$0.805) — currently -21.7%, not yet triggered |
| SLB260821C00052000 | $1.65 | $2.19 | +$1,080.00 | 28 | Close at -50% or +50-100% gain |

No options are within 5 DTE going into next week (all 28 DTE as of today).

### What Worked
- Multi-source-confirmed sector catalysts (XLE/XOP oil-supply-shock thesis) produced the week's best-documented entries with clean R:R math shown at entry.
- Diversifying the energy book's catalyst source (SLB's idiosyncratic post-earnings beat, distinct from pure oil-price beta) worked immediately — it's the week's best performer (+32.7%) within hours of entry.
- Discipline on HOLD calls: multiple research cycles correctly sat out semis/AI (GOOGL/TSLA post-earnings) as genuinely two-way/unresolved rather than forcing an ambiguous trade.
- Every entry documented the Rule 3 (8%-of-equity max loss) calculation explicitly before sizing, and every stock leg got a real GTC trailing stop placed immediately on fill.
- Bot ended the week essentially flat (-0.02%) while outperforming the S&P 500 (-0.42%) during a genuinely volatile week (Iran/Hormuz escalation, oil >$100, Mag7 selloff).

### What Didn't Work
- Zero trades closed all week — no realized P&L data yet to actually evaluate the strategy's edge; every number this review is unrealized/mark-to-market.
- Sector concentration: all 5 positions currently open are the same oil-supply-shock thesis (XLE/XOP/SLB all energy-correlated) — flagged repeatedly in RESEARCH-LOG across 3+ cycles but never resolved by diversifying into a genuinely uncorrelated sector.
- XLE 61C call is down -21.7%, roughly halfway to its -50% stop, and has been flagged as "the position to watch" for two consecutive days without a plan beyond waiting for the mechanical trigger.
- Capital deployment sat at 65-69% most of the week, below the 85-100% target — deployment gap is a direct drag on hitting the $50k target on schedule.
- Pace: after 20% of the challenge timeline, 0% of the profit target has been captured — the challenge requires a materially higher weekly return than what a single-sector, mostly-long-calls book has produced so far.

### Key Lessons
- A clean, multi-source-confirmed catalyst (XLE, then SLB) is achievable multiple times a week — the entry process itself is working. The gap is diversification and deployment, not catalyst-finding.
- Concentrating 5-of-5 open positions in one macro thesis (oil/energy) means a single de-escalation headline (ceasefire, Strait of Hormuz reopening) could hit the entire book simultaneously — this is a real, not theoretical, tail risk given how two-way the Iran conflict has already proven this month.
- Options sleeves add meaningful volatility to weekly returns in both directions (SLB +32.7% vs. XLE61C -21.7% within the same week, same sector) — they're doing their job as a leveraged lever toward the target, but only pay off with more/faster diversification of underlying catalysts, not more of the same one.

### Adjustments for Next Week
- Actively source a non-energy catalyst next week (a distinct sector/idiosyncratic-earnings setup) before adding any more energy exposure — Core Rule 10 logic (exit a sector after 2 failed trades) should extend in spirit to "stop concentrating after N correlated adds" even though no trade has technically failed yet.
- Push capital deployment from ~65-69% toward the 85-100% target — either larger sizing on the next qualifying non-energy setup or an additional defined-risk sleeve.
- Set a firm decision point on XLE260821C00061000 by Monday: either it recovers meaningfully or it gets closed at/near the -50% mechanical trigger rather than left as an open watch item for a third day.
- Given the pace gap (-$19 vs. an on-pace +$10,000), lean toward the more aggressive end of Rule 2/3 sizing on the next clean catalyst, per THE CHALLENGE section's explicit guidance for behind-pace weeks — without loosening the 8%-of-equity hard cap.

### Overall Grade: C+

Process discipline (documented catalysts, Rule 3 math, real stops) is solid and the bot slightly outperformed the S&P 500 this week. Grade is capped by zero closed trades to validate real edge, unresolved single-sector concentration flagged repeatedly without action, and a widening gap to the required pace for the $150,000 target.
