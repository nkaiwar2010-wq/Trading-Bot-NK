# Oasis

A fully autonomous swing-trading agent built on Claude Code. Five scheduled
cloud routines run each weekday, reading and writing state as markdown files
committed to `main`. **Paper trading only — no real money.**

Strategy, architecture, and full setup guide live outside this repo; this
README is the quickstart.

## Layout
- `CLAUDE.md` — agent rulebook, auto-loaded every session
- `scripts/` — the only way to touch the outside world (Alpaca, Perplexity, ClickUp)
- `memory/` — the agent's persistent state, committed to git
- `.claude/commands/` — local ad-hoc slash commands (uses `.env`)
- `routines/` — cloud routine prompts (production path, uses routine env vars)

## Local setup
```bash
cp env.template .env
# fill in your Alpaca paper keys, Perplexity key, ClickUp keys
```
Open this repo in Claude Code and run `/portfolio` to smoke-test — you
should see account equity and positions print cleanly.

## Cloud setup
See `routines/README.md`.

## Current challenge
Grow the account $50,000+ (to $150,000+ equity) by 2026-08-19 (started
2026-07-19). Paper money only, no real funds at risk.

## Hard rules (quick reference)
- HARD CAP, never bends: no single trade may risk more than 8% of current
  equity.
- Stocks and options both permitted (including uncovered/naked single-leg
  options) — a deliberate lever for the challenge target, not just a test.
- Up to 8 open positions, max 30% equity notional each (subject to the 8%
  loss cap). NO weekly trade-count cap for the duration of the challenge.
- Target 85-100% capital deployed.
- Stocks: real 10% GTC trailing stop on every position. Cut losers at -7%.
  Tighten stops at +15%/+20%.
- Options: close longs at -50% premium; close naked shorts if value doubles
  or strike is breached; no new positions inside 7 DTE.
- Bias toward action — HOLD only when nothing clears the catalyst + loss-cap
  bar.

Full rules: `memory/TRADING-STRATEGY.md`.
