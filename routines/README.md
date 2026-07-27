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

**v3 (2026-07-27):** entries/exits now run as a **continuous GitHub
Actions daemon** (`scripts/mirage_daemon.py`), not a Claude Code cloud
routine — Claude Code's `RemoteTrigger` scheduler has a hard 1-hour
minimum firing interval, which was v2's ceiling and still too slow for
real day-trading. The daemon runs deterministic code (Gap-and-Go +
Opening Range Breakout + VWAP, stock-only for now) against Alpaca's own
`movers`/`most-actives`/`bars` endpoints, polling every ~60 seconds in a
single long-lived job from market open to a safety cutoff before the
still-mandatory EOD close. See `memory/mirage/STRATEGY.md` for the full
model and why each prior version was replaced.

| Component | Type | Schedule | Purpose |
|---|---|---|---|
| `.github/workflows/mirage-daemon.yml` → `scripts/mirage_daemon.py` | GitHub Actions (not Claude Code) | cron `30 13 * * 1-5` UTC (8:30am Chicago) start, runs continuously to ~2:30pm Chicago | Manage open positions (VWAP-loss/target exit), screen movers/most-actives, confirm ORB, trade if it clears the checklist. Commits only on an actual entry/exit. Requires repo secrets `MIRAGE_ALPACA_API_KEY` / `MIRAGE_ALPACA_SECRET_KEY`. |
| mirage-eod-close.md | Claude Code cloud routine | `45 19 * * 1-5` UTC / `45 14 * * 1-5` Chicago | MANDATORY: force-close everything, log the day's realized results. Unchanged since v1 — the hard backstop regardless of what the daemon did. |
| mirage-evening-research.md | Claude Code cloud routine | `0 21 * * 1-5` UTC / `0 16 * * 1-5` Chicago | Research-only (no trading): builds tomorrow's watchlist from earnings/econ-calendar/overnight news via WebSearch. Always commits. |

Retired (disabled, not deleted): mirage-morning-entry.md,
mirage-midday-check.md (v1), mirage-intraday-scan.md (v2, hourly Claude
Code routine) — all superseded by the daemon above. Running the v2
hourly routine alongside the daemon would mean two independent traders
fighting over the same account/position limits, so it stays off.

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
