#!/usr/bin/env python3
"""Mirage intraday daemon — continuous, deterministic day-trading loop.

Runs once per trading day as a single long-lived GitHub Actions job
(started at market open). No LLM calls in the loop; encodes the
Gap-and-Go + Opening-Range-Breakout + VWAP rules from
memory/mirage/STRATEGY.md directly in code, polling Alpaca every
POLL_SECONDS. Stock-only, long-only for v1 (movers/most-actives are
stock screeners anyway; options can be added once this is proven).

State (today's attempted symbols) lives in memory for the run. If the
process restarts mid-day, it re-derives already-attempted symbols from
today's TRADE-LOG.md entries via the DAEMON_ENTRY marker.
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib import request as urlrequest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADE_LOG = os.path.join(ROOT, "memory", "mirage", "TRADE-LOG.md")

API = os.environ.get("ALPACA_ENDPOINT", "https://paper-api.alpaca.markets/v2")
DATA = os.environ.get("ALPACA_DATA_ENDPOINT", "https://data.alpaca.markets/v2")
DATA_ROOT = DATA[: -len("/v2")] if DATA.endswith("/v2") else DATA
KEY = os.environ["ALPACA_API_KEY"]
SECRET = os.environ["ALPACA_SECRET_KEY"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_URL = f"https://x-access-token:{GITHUB_TOKEN}@github.com/nkaiwar2010-wq/Trading-Bot-NK.git"

HEADERS = {"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SECRET}

# --- Rules, mirroring memory/mirage/STRATEGY.md ---
MAX_LOSS_PCT = 0.08          # Rule 1 hard cap, never bends
MAX_POSITIONS = 4
MAX_NOTIONAL_PCT = 0.40
STOP_PCT = 0.03              # fallback stop distance if OR extreme is looser
MIN_RR = 2.0
GAP_MIN_PCT = 3.0
POLL_SECONDS = 60
STOP_NEW_ENTRIES_AFTER_UTC = (19, 15)   # 2:15pm Chicago — buffer before the
                                        # separate mandatory 2:45pm EOD-close
                                        # routine; this daemon never force-closes
                                        # itself, that routine remains the backstop.
HARD_EXIT_AFTER_UTC = (19, 30)          # stop the loop entirely, well under the
                                        # 6-hour GitHub Actions job limit


def log(msg):
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC] {msg}", flush=True)


def api(method, path, body=None):
    base = DATA if path.startswith("/stocks") or path.startswith("/v1beta1") else API
    url = (DATA_ROOT + path) if path.startswith("/v1beta1") else (base + path)
    headers = dict(HEADERS)
    payload = None
    if body is not None:
        payload = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urlrequest.Request(url, data=payload, headers=headers, method=method)
    try:
        with urlrequest.urlopen(req, timeout=20) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except Exception as e:
        log(f"API {method} {url} FAILED: {e}")
        return None


def get_account():
    return api("GET", "/account")


def get_positions():
    return api("GET", "/positions") or []


def get_orders(status="open"):
    return api("GET", f"/orders?status={status}") or []


def get_bars(symbol, timeframe="5Min", limit=30):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    resp = api("GET", f"/stocks/{symbol}/bars?timeframe={timeframe}&start={today}T00:00:00Z&limit={limit}&adjustment=raw&feed=iex")
    if not resp:
        return []
    return resp.get("bars") or []


def get_movers(top=10):
    resp = api("GET", f"/v1beta1/screener/stocks/movers?top={top}")
    if not resp:
        return []
    return (resp.get("gainers") or []) + (resp.get("losers") or [])


def get_most_actives(top=10):
    resp = api("GET", f"/v1beta1/screener/stocks/most-actives?top={top}&by=volume")
    if not resp:
        return []
    return resp.get("most_actives") or []


def get_quote(symbol):
    resp = api("GET", f"/stocks/{symbol}/quotes/latest?feed=iex")
    if not resp:
        return None
    return resp.get("quote")


def place_order(body):
    return api("POST", "/orders", body=body)


def close_position(symbol):
    return api("DELETE", f"/positions/{symbol}")


def cancel_order(order_id):
    return api("DELETE", f"/orders/{order_id}")


def opening_range(bars):
    """High/low of the first 1-3 five-minute bars after 13:30 UTC (8:30am Chicago)."""
    session_bars = [b for b in bars if b["t"][11:16] >= "13:30"]
    first = session_bars[:3]
    if not first:
        return None, None
    return max(b["h"] for b in first), min(b["l"] for b in first)


def confirmed_breakout(bars, or_high, or_low):
    """A 5-min bar must have CLOSED beyond the opening range, not just wicked it."""
    session_bars = [b for b in bars if b["t"][11:16] >= "13:30"]
    if len(session_bars) < 4:
        return None  # not enough bars yet to have a range + a confirming close
    latest = session_bars[-1]
    if latest["c"] > or_high:
        return "long", latest["c"]
    return None  # short side intentionally unsupported in v1 (long-only)


def vwap_loss_signal(bars):
    """True if price was above VWAP and the latest bar closed back below it
    on above-average volume — an early thesis-break signal."""
    session_bars = [b for b in bars if b["t"][11:16] >= "13:30"]
    if len(session_bars) < 3:
        return False
    latest = session_bars[-1]
    prior = session_bars[-2]
    avg_vol = sum(b["v"] for b in session_bars[:-1]) / max(1, len(session_bars) - 1)
    was_above = prior["c"] >= prior["vw"]
    now_below = latest["c"] < latest["vw"]
    volume_spike = latest["v"] > avg_vol * 1.3
    return was_above and now_below and volume_spike


def already_attempted_today():
    """Resilience: if this process restarted mid-day, recover today's
    already-attempted symbols from TRADE-LOG's DAEMON_ENTRY markers."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    attempted = set()
    if not os.path.exists(TRADE_LOG):
        return attempted
    with open(TRADE_LOG) as f:
        for line in f:
            m = re.match(r"<!-- DAEMON_ENTRY: (\S+) \S+ (\S+) -->", line)
            if m and m.group(2) == today:
                attempted.add(m.group(1))
    return attempted


def append_trade_log(entry_markdown):
    with open(TRADE_LOG, "a") as f:
        f.write("\n" + entry_markdown + "\n")


def git_commit_and_push(message):
    def run(cmd):
        return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)

    run(["git", "config", "user.name", "Mirage Daemon"])
    run(["git", "config", "user.email", "mirage-bot@noreply.local"])
    run(["git", "add", "memory/mirage/TRADE-LOG.md"])
    commit = run(["git", "commit", "-m", message])
    if commit.returncode != 0:
        log(f"nothing to commit or commit failed: {commit.stdout}{commit.stderr}")
        return
    push = run(["git", "push", REPO_URL, "HEAD:main"])
    if push.returncode != 0:
        log(f"push failed, rebasing and retrying: {push.stderr}")
        run(["git", "pull", "--rebase", REPO_URL, "main"])
        push2 = run(["git", "push", REPO_URL, "HEAD:main"])
        if push2.returncode != 0:
            log(f"push retry FAILED: {push2.stderr}")
        else:
            log("push succeeded on retry")
    else:
        log(f"committed and pushed: {message}")


def rule1_stock_qty(equity, entry_price, stop_price):
    max_loss = equity * MAX_LOSS_PCT
    stop_distance = abs(entry_price - stop_price)
    if stop_distance <= 0:
        return 0
    qty_by_risk = int(max_loss // stop_distance)
    qty_by_notional = int((equity * MAX_NOTIONAL_PCT) // entry_price)
    return max(0, min(qty_by_risk, qty_by_notional))


def utc_hm():
    n = datetime.now(timezone.utc)
    return n.hour, n.minute


def past(cutoff):
    return utc_hm() >= cutoff


def manage_positions(equity):
    for pos in get_positions():
        symbol = pos["symbol"]
        if pos.get("asset_class") != "us_equity":
            continue  # v1 is stock-only; leave any option position for the
                       # hourly Claude routine / EOD-close to handle
        bars = get_bars(symbol)
        if not bars:
            continue
        entry = float(pos["avg_entry_price"])
        current = float(pos["current_price"])
        unrealized_pct = float(pos["unrealized_plpc"])
        reason = None
        if vwap_loss_signal(bars):
            reason = "VWAP loss on volume spike (thesis break)"
        elif unrealized_pct >= (MIN_RR * STOP_PCT):
            reason = f"target reached ({unrealized_pct:.1%}, >= {MIN_RR}:1 R:R)"
        if reason:
            log(f"Closing {symbol}: {reason}")
            close_position(symbol)
            for o in get_orders("open"):
                if o["symbol"] == symbol:
                    cancel_order(o["id"])
            pnl = float(pos["unrealized_pl"])
            entry_line = (
                f"<!-- DAEMON_EXIT: {symbol} {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} -->\n"
                f"### {datetime.now(timezone.utc).strftime('%b %d %H:%M UTC')} — Intraday Daemon Exit\n"
                f"**{symbol}** closed @ ~${current:.2f} | entry ${entry:.2f} | "
                f"realized P&L ${pnl:.2f} ({unrealized_pct:.1%}) | reason: {reason}"
            )
            append_trade_log(entry_line)
            git_commit_and_push(f"mirage daemon exit {symbol} {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")


def screen_new_entry(equity, attempted, open_count):
    if open_count >= MAX_POSITIONS:
        return
    candidates = get_movers(10) + get_most_actives(10)
    seen = set()
    for c in candidates:
        symbol = c.get("symbol")
        if not symbol or symbol in seen or symbol in attempted:
            continue
        seen.add(symbol)
        pct_change = c.get("percent_change") or c.get("change_percent") or 0
        try:
            pct_change = float(pct_change)
        except (TypeError, ValueError):
            pct_change = 0
        if abs(pct_change) < GAP_MIN_PCT:
            continue
        bars = get_bars(symbol)
        if not bars:
            continue
        or_high, or_low = opening_range(bars)
        if or_high is None:
            continue
        breakout = confirmed_breakout(bars, or_high, or_low)
        if not breakout:
            continue
        side, breakout_price = breakout
        quote = get_quote(symbol)
        if not quote:
            continue
        entry_price = quote.get("ap") or breakout_price
        stop_price = min(or_low, entry_price * (1 - STOP_PCT))
        qty = rule1_stock_qty(equity, entry_price, stop_price)
        if qty <= 0:
            continue
        target_price = entry_price + MIN_RR * (entry_price - stop_price)
        log(f"ENTRY {symbol}: qty={qty} entry~{entry_price:.2f} stop={stop_price:.2f} target={target_price:.2f}")
        order = place_order({
            "symbol": symbol, "qty": str(qty), "side": "buy",
            "type": "market", "time_in_force": "day",
        })
        if not order:
            continue
        place_order({
            "symbol": symbol, "qty": str(qty), "side": "sell",
            "type": "stop", "stop_price": f"{stop_price:.2f}", "time_in_force": "day",
        })
        attempted.add(symbol)
        risk = qty * abs(entry_price - stop_price)
        now = datetime.now(timezone.utc)
        entry_line = (
            f"<!-- DAEMON_ENTRY: {symbol} long {now.strftime('%Y-%m-%d')} -->\n"
            f"### {now.strftime('%b %d %H:%M UTC')} — Intraday Daemon Entry\n"
            f"**{symbol}** long {qty} sh @ ~${entry_price:.2f} | stop ${stop_price:.2f} | "
            f"target ${target_price:.2f} ({MIN_RR}:1) | gap {pct_change:.1f}%, ORB confirmed above ${or_high:.2f} | "
            f"Rule 1: {qty} x ${abs(entry_price - stop_price):.2f} = ${risk:.2f} "
            f"({risk / equity:.1%} of ${equity:,.0f} equity, cap {MAX_LOSS_PCT:.0%})"
        )
        append_trade_log(entry_line)
        git_commit_and_push(f"mirage daemon entry {symbol} {now.strftime('%Y-%m-%d %H:%M')} UTC")
        return  # one new entry per loop iteration is plenty; re-evaluate next cycle


def main():
    log("Mirage intraday daemon starting")
    attempted = already_attempted_today()
    log(f"already-attempted symbols recovered from TRADE-LOG: {attempted or 'none'}")
    while True:
        if past(HARD_EXIT_AFTER_UTC):
            log("hard exit time reached, ending daemon for today")
            break
        account = get_account()
        if not account:
            log("account fetch failed, sleeping and retrying")
            time.sleep(POLL_SECONDS)
            continue
        equity = float(account["equity"])
        positions = get_positions()
        manage_positions(equity)
        if not past(STOP_NEW_ENTRIES_AFTER_UTC):
            screen_new_entry(equity, attempted, len(positions))
        else:
            log("past new-entry cutoff (2:15pm Chicago) — management only, no new entries")
        time.sleep(POLL_SECONDS)
    log("daemon loop ended; mandatory EOD-close routine remains the backstop at 2:45pm Chicago")


if __name__ == "__main__":
    sys.exit(main())
