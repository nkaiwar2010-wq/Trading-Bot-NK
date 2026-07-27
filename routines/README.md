# Cloud Routines

This repo runs **two independent bots** on two separate Alpaca paper
accounts, sharing this repo and infrastructure but never each other's
memory or capital.

## Oasis (swing/options, $100,000 account)

These five prompts are pasted verbatim into Claude Code cloud routines — this
is the production path. Do not paraphrase; the environment-variable check
block and the commit-and-push step are load-bearing.

| File | Cron (America/Chicago) | Purpose |
|---|---|---|
| pre-market.md | `0 6 * * 1-5` | Research catalysts, write trade ideas |
| market-open.md | `30 8 * * 1-5` | Execute planned trades, set trailing stops |
| midday.md | `0 12 * * 1-5` | Cut losers, tighten stops on winners |
| daily-summary.md | `0 15 * * 1-5` | Snapshot portfolio, send recap |
| weekly-review.md | `0 16 * * 5` | Compute weekly stats, grade, adjust strategy |

## Mirage (day-trading, $50,000 account)

Separate Alpaca paper account (PA3ER1AHRYXX), separate cloud environment
with its own credentials, separate memory files under `memory/mirage/`.
Core rule: every position opened must close the same day — the EOD-close
routine force-closes everything before market close, no exceptions.

**v2 (2026-07-27):** replaced the original 3x/day WebSearch-catalyst model
with a near-continuous, screener-driven model. WebSearch can't see live
intraday tape, so entries now come from Alpaca's own `movers`/
`most-actives`/`bars` endpoints (Gap-and-Go confirmed by Opening Range
Breakout, managed by VWAP) instead of news search. See
`memory/mirage/STRATEGY.md` for the full model.

| File | Cron (UTC) | Cron (America/Chicago) | Purpose |
|---|---|---|---|
| mirage-intraday-scan.md | `*/5 13-19 * * 1-5` | every 5 min, 8:30am-2:45pm (self-guards to the real 8:30-2:44 window) | Manage open positions (VWAP-loss/target exit), screen movers/most-actives, confirm ORB, trade if it clears the checklist. Commits only when something changes. |
| mirage-eod-close.md | `45 19 * * 1-5` | `45 14 * * 1-5` | MANDATORY: force-close everything, log the day's realized results. Unchanged from v1. |
| mirage-evening-research.md | `0 21 * * 1-5` | `0 16 * * 1-5` | Research-only (no trading): builds tomorrow's watchlist from earnings/econ-calendar/overnight news via WebSearch. Always commits. |

Retired (v1, disabled): mirage-morning-entry.md, mirage-midday-check.md —
superseded by mirage-intraday-scan.md above.

Setup steps for each routine (Part 7 of the guide):
1. Install the Claude GitHub App on this repo.
2. New Routine → select this repo, branch `main`.
3. Add all required env vars (see env.template for names) — never a `.env` file.
4. Toggle on "Allow unrestricted branch pushes".
5. Set the cron schedule + timezone from the table above.
6. Paste the corresponding `.md` file's contents verbatim into the prompt field.
7. Save, then click "Run now" once to verify before trusting the schedule.

This repo runs in **paper trading mode** (Alpaca paper endpoint) — no real
money is at risk.
