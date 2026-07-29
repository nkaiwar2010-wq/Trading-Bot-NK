#!/usr/bin/env python3
"""Mirage strategy backtest — runs the exact live entry/exit rules from
scripts/mirage_daemon.py against historical bars, across many days at once,
instead of waiting for real trading days to accumulate.

Honest limitation: Alpaca's `movers`/`most-actives` screener only works for
the CURRENT day, not historical dates, so this can't perfectly replay "what
would today's screener have shown on 2026-06-15." Instead it checks a fixed
watchlist of historically volatile, liquid tickers each day for a
qualifying gap. This backtests the STRATEGY LOGIC (gap % + ORB + VWAP) on a
representative universe, not an exact replay of which stocks the live
screener would have surfaced.

Usage: python scripts/mirage_backtest.py [days_back]
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from urllib import request as urlrequest

KEY = os.environ["ALPACA_API_KEY"]
SECRET = os.environ["ALPACA_SECRET_KEY"]
HEADERS = {"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SECRET}
DATA = "https://data.alpaca.markets/v2"

# Liquid, historically volatile tickers -- not a perfect stand-in for the
# live screener's penny-stock-heavy output, but real, data-available names
# suitable for testing the gap/ORB/VWAP logic itself across many days.
WATCHLIST = [
    "TSLA", "NVDA", "AMD", "PLTR", "SOFI", "RIOT", "MARA", "COIN", "SMCI",
    "MSTR", "ARM", "NIO", "LCID", "RIVN", "UPST", "SOXL", "TQQQ", "SQQQ",
    "SNAP", "AFRM", "CVNA", "DKNG", "HOOD", "IONQ", "RBLX", "SHOP", "ROKU",
    "PYPL", "U", "NET", "CRWD", "PANW", "ENPH", "FSLR", "AI", "PATH", "GME",
    "AMC", "BBBY", "SPCE",
]

MAX_LOSS_PCT = 0.04
MAX_NOTIONAL_PCT = 0.20
STOP_PCT = 0.03
MIN_RR = 2.0
GAP_MIN_PCT = 3.0
GAP_MAX_PCT = 20.0
START_EQUITY = 50000.0
REQUIRE_VOLUME_CONFIRM = os.environ.get("REQUIRE_VOLUME_CONFIRM", "0") == "1"


def api_get(path):
    req = urlrequest.Request(DATA + path, headers=HEADERS)
    try:
        with urlrequest.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  API error {path}: {e}", file=sys.stderr)
        return None


def get_daily_bars(symbol, start, end):
    resp = api_get(f"/stocks/{symbol}/bars?timeframe=1Day&start={start}&end={end}&adjustment=raw&feed=iex&limit=200")
    return (resp or {}).get("bars") or []


def get_intraday_bars(symbol, day):
    resp = api_get(f"/stocks/{symbol}/bars?timeframe=5Min&start={day}T00:00:00Z&end={day}T23:59:00Z&adjustment=raw&feed=iex&limit=200")
    return (resp or {}).get("bars") or []


def opening_range(bars, session_start="13:30"):
    session = [b for b in bars if b["t"][11:16] >= session_start]
    first = session[:3]
    if not first:
        return None, None, session
    return max(b["h"] for b in first), min(b["l"] for b in first), session


def confirmed_breakout(session_bars, or_high, require_volume=False):
    if len(session_bars) < 4:
        return None
    latest = session_bars[-1]
    if latest["c"] <= or_high:
        return None
    if require_volume:
        prior = session_bars[:-1]
        avg_vol = sum(b["v"] for b in prior) / max(1, len(prior))
        if latest["v"] < avg_vol * 1.2:
            return None
    return latest["c"]


def simulate_trade(session_bars, entry_idx, entry_price, stop_price, target_price):
    """Walk forward through the rest of the day's bars applying stop/target/
    VWAP-loss exit logic, same priority as the live daemon. Returns
    (exit_price, reason)."""
    avg_vol_window = session_bars[:entry_idx] or session_bars[:1]
    avg_vol = sum(b["v"] for b in avg_vol_window) / max(1, len(avg_vol_window))
    was_above_vwap = True
    for b in session_bars[entry_idx + 1:]:
        if b["l"] <= stop_price:
            return stop_price, "stop hit"
        if b["h"] >= target_price:
            return target_price, "target hit"
        now_below = b["c"] < b["vw"]
        vol_spike = b["v"] > avg_vol * 1.3
        if was_above_vwap and now_below and vol_spike:
            return b["c"], "VWAP loss exit"
        was_above_vwap = b["c"] >= b["vw"]
    return session_bars[-1]["c"], "EOD force-close"


def rule1_qty(equity, entry_price, stop_price):
    max_loss = equity * MAX_LOSS_PCT
    stop_distance = abs(entry_price - stop_price)
    if stop_distance <= 0:
        return 0
    qty_by_risk = int(max_loss // stop_distance)
    qty_by_notional = int((equity * MAX_NOTIONAL_PCT) // entry_price)
    return max(0, min(qty_by_risk, qty_by_notional))


def main():
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days_back + 10)  # pad for weekends/holidays

    print(f"Backtesting {len(WATCHLIST)} tickers over ~{days_back} trading days ({start} to {end})")
    print(f"Rules: gap {GAP_MIN_PCT}-{GAP_MAX_PCT}%, stop {STOP_PCT:.0%}/OR-extreme (tighter), "
          f"target {MIN_RR}:1, max loss {MAX_LOSS_PCT:.0%} equity, max notional {MAX_NOTIONAL_PCT:.0%}\n")

    equity = START_EQUITY
    trades = []

    for symbol in WATCHLIST:
        daily = get_daily_bars(symbol, start.isoformat(), end.isoformat())
        if len(daily) < 2:
            continue
        for i in range(1, len(daily)):
            prev_close = daily[i - 1]["c"]
            day_bar = daily[i]
            day = day_bar["t"][:10]
            gap_pct = (day_bar["o"] - prev_close) / prev_close * 100
            if not (GAP_MIN_PCT <= abs(gap_pct) <= GAP_MAX_PCT):
                continue
            if gap_pct < 0:
                continue  # long-only, matches live daemon
            intraday = get_intraday_bars(symbol, day)
            or_high, or_low, session = opening_range(intraday)
            if or_high is None:
                continue
            for idx in range(3, len(session)):
                breakout_price = confirmed_breakout(session[:idx + 1], or_high, require_volume=REQUIRE_VOLUME_CONFIRM)
                if not breakout_price:
                    continue
                entry_price = breakout_price
                stop_price = max(or_low, entry_price * (1 - STOP_PCT))
                qty = rule1_qty(equity, entry_price, stop_price)
                if qty <= 0:
                    break
                target_price = entry_price + MIN_RR * (entry_price - stop_price)
                exit_price, reason = simulate_trade(session, idx, entry_price, stop_price, target_price)
                pnl = qty * (exit_price - entry_price)
                equity += pnl
                trades.append({
                    "symbol": symbol, "day": day, "gap_pct": round(gap_pct, 1),
                    "entry": round(entry_price, 4), "exit": round(exit_price, 4),
                    "qty": qty, "pnl": round(pnl, 2), "reason": reason,
                    "equity_after": round(equity, 2),
                })
                break  # one trade per symbol per day, matches live daemon

    if not trades:
        print("No qualifying trades found in this window/watchlist.")
        return

    wins = [t for t in trades if t["pnl"] > 0]
    losses = [t for t in trades if t["pnl"] <= 0]
    total_pnl = sum(t["pnl"] for t in trades)

    print(f"=== RESULTS: {len(trades)} trades ===")
    print(f"Win rate: {len(wins)}/{len(trades)} ({len(wins)/len(trades):.1%})")
    if wins:
        print(f"Avg win: ${sum(t['pnl'] for t in wins)/len(wins):.2f}")
    if losses:
        print(f"Avg loss: ${sum(t['pnl'] for t in losses)/len(losses):.2f}")
    print(f"Total P&L: ${total_pnl:.2f} ({total_pnl/START_EQUITY:.1%} of starting equity)")
    print(f"Final equity: ${equity:.2f}\n")

    print("=== By exit reason ===")
    for reason in set(t["reason"] for t in trades):
        subset = [t for t in trades if t["reason"] == reason]
        print(f"  {reason}: {len(subset)} trades, ${sum(t['pnl'] for t in subset):.2f} total, "
              f"{sum(1 for t in subset if t['pnl'] > 0)}/{len(subset)} won")

    print("\n=== By gap-size bucket ===")
    buckets = [(3, 7), (7, 12), (12, 20)]
    for lo, hi in buckets:
        subset = [t for t in trades if lo <= t["gap_pct"] < hi]
        if not subset:
            continue
        w = sum(1 for t in subset if t["pnl"] > 0)
        print(f"  {lo}-{hi}%: {len(subset)} trades, {w}/{len(subset)} won ({w/len(subset):.0%}), "
              f"${sum(t['pnl'] for t in subset):.2f} total")

    print("\n=== All trades ===")
    for t in trades:
        print(f"  {t['day']} {t['symbol']}: gap {t['gap_pct']}%, entry ${t['entry']}, "
              f"exit ${t['exit']} ({t['reason']}), qty {t['qty']}, P&L ${t['pnl']}")


if __name__ == "__main__":
    main()
