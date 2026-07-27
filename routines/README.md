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

| File | Cron (America/Chicago) | Purpose |
|---|---|---|
| mirage-morning-entry.md | `30 8 * * 1-5` | Research today's specific catalysts, open positions with real stops |
| mirage-midday-check.md | `0 12 * * 1-5` | Take early profit/cut broken theses; optionally add a fresh same-day catalyst |
| mirage-eod-close.md | `45 14 * * 1-5` | MANDATORY: force-close everything, log the day's realized results |

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
