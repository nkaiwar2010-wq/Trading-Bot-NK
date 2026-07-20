# trading-bot

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

## Hard rules (quick reference)
- Stocks only, never options.
- Max 5-6 open positions, max 20% of equity each.
- Max 3 new trades per week, 75-85% capital deployed.
- Every position gets a real 10% GTC trailing stop.
- Cut losers at -7%. Tighten stops at +15%/+20%.

Full rules: `memory/TRADING-STRATEGY.md`.
