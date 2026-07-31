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
MAX_LOSS_PCT = 0.04          # halved 2026-07-27 after day-1 losses (was 0.08)
                              # while the strategy is still proving itself
MAX_POSITIONS = 4
MAX_NOTIONAL_PCT = 0.20      # halved 2026-07-27 after day-1 losses (was 0.40)
STOP_PCT = 0.03              # fallback stop distance if OR extreme is looser
MIN_RR = 2.0
GAP_MIN_PCT = 3.0
GAP_MAX_PCT = 20.0           # ceiling added after day-1 live data: the two
                              # losers (2026-07-27) had already gapped 85.8%
                              # and 64.6% before entry — buying an already-
                              # extended move is a different (worse) trade
                              # than a fresh breakout. Research consensus
                              # favors 3-7% gaps; 20% gives margin without
                              # chasing exhausted moves. Revisit with more data.
POLL_SECONDS = 60
START_UTC = (13, 25)                    # a few min before 8:30am Chicago open;
                                        # a manual/misfired run before this exits
                                        # immediately instead of spinning for hours
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


def get_fills_today(symbol):
    """Today's actual fills for a symbol from Alpaca's activity ledger --
    authoritative even when a position closes via a mechanism the daemon
    didn't initiate itself (e.g. a standing stop order filling on
    Alpaca's side independent of the poll loop)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    resp = api("GET", f"/account/activities/FILL?date={today}")
    if not resp:
        return []
    return [f for f in resp if f.get("symbol") == symbol]


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


def get_order(order_id):
    return api("GET", f"/orders/{order_id}")


def close_position(symbol):
    return api("DELETE", f"/positions/{symbol}")


def cancel_order(order_id):
    return api("DELETE", f"/orders/{order_id}")


def wait_for_fill(order_id, timeout_seconds=15, poll_seconds=1):
    """Poll an order until it's filled (or timeout). Returns
    (filled_qty, filled_avg_price) -- both 0 if it never filled in time.
    Placing a protective stop before the buy actually fills risks Alpaca
    rejecting it for insufficient position quantity — this closes that
    race condition. filled_avg_price matters separately: a fast-moving or
    thin stock can fill far from the quote used to size the trade (seen
    live 2026-07-29: NNNN quoted ~$11.65, filled at $12.90-13.26 avg, an
    ~11-14% slip) -- stop/target must be computed from the REAL fill
    price, not the pre-fill quote, or the whole risk model is wrong."""
    waited = 0
    while waited < timeout_seconds:
        order = get_order(order_id)
        if order and order.get("status") == "filled":
            return int(float(order.get("filled_qty", 0))), float(order.get("filled_avg_price") or 0)
        time.sleep(poll_seconds)
        waited += poll_seconds
    log(f"order {order_id} did not report 'filled' within {timeout_seconds}s")
    order = get_order(order_id)
    if not order:
        return 0, 0.0
    return int(float(order.get("filled_qty", 0))), float(order.get("filled_avg_price") or 0)


def wait_for_close(symbol, timeout_seconds=15, poll_seconds=1):
    """Poll until the position is actually gone. Returns True if confirmed
    closed, False if it timed out still showing a position — a liquidation
    call can fail (rejected order, etc.) and must not be assumed to have
    worked just because it was submitted."""
    waited = 0
    while waited < timeout_seconds:
        positions = get_positions()
        if not any(p["symbol"] == symbol for p in positions):
            return True
        time.sleep(poll_seconds)
        waited += poll_seconds
    return False


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
    open_orders = get_orders("open")
    for pos in get_positions():
        symbol = pos["symbol"]
        if pos.get("asset_class") != "us_equity":
            continue  # v1 is stock-only; leave any option position for the
                       # hourly Claude routine / EOD-close to handle
        entry = float(pos["avg_entry_price"])
        current = float(pos["current_price"])
        qty = pos["qty"]
        has_stop = any(
            o["symbol"] == symbol and o["side"] == "sell" and o["type"] == "stop"
            for o in open_orders
        )
        if not has_stop:
            fallback_stop = round(min(entry, current) * (1 - STOP_PCT), 2)
            log(f"SAFETY NET: {symbol} has no protective stop — placing one now at {fallback_stop}")
            place_order({
                "symbol": symbol, "qty": str(qty), "side": "sell",
                "type": "stop", "stop_price": f"{fallback_stop:.2f}", "time_in_force": "day",
            })
        bars = get_bars(symbol)
        if not bars:
            continue
        unrealized_pct = float(pos["unrealized_plpc"])
        reason = None
        if vwap_loss_signal(bars):
            reason = "VWAP loss on volume spike (thesis break)"
        elif unrealized_pct >= (MIN_RR * STOP_PCT):
            reason = f"target reached ({unrealized_pct:.1%}, >= {MIN_RR}:1 R:R)"
        if reason:
            log(f"Closing {symbol}: {reason}")
            # Cancel existing orders FIRST — an open stop order reserves the
            # shares (qty_available drops to 0), which can make the
            # liquidation call below fail. Only after cancelling do we
            # attempt the close, and only log/commit if it's CONFIRMED,
            # not just attempted (a prior version logged "closed" even
            # when the liquidation silently failed, corrupting the record).
            for o in open_orders:
                if o["symbol"] == symbol:
                    cancel_order(o["id"])
            close_position(symbol)
            if not wait_for_close(symbol):
                log(f"{symbol} close did NOT confirm within timeout — position "
                    f"likely still open; re-placing a protective stop so it "
                    f"isn't left naked, will retry the close next cycle")
                fallback_stop = round(min(entry, current) * (1 - STOP_PCT), 2)
                place_order({
                    "symbol": symbol, "qty": str(qty), "side": "sell",
                    "type": "stop", "stop_price": f"{fallback_stop:.2f}", "time_in_force": "day",
                })
                continue
            pnl = float(pos["unrealized_pl"])
            entry_line = (
                f"<!-- DAEMON_EXIT: {symbol} {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} -->\n"
                f"### {datetime.now(timezone.utc).strftime('%b %d %H:%M UTC')} — Intraday Daemon Exit\n"
                f"**{symbol}** closed @ ~${current:.2f} | entry ${entry:.2f} | "
                f"realized P&L ${pnl:.2f} ({unrealized_pct:.1%}) | reason: {reason}"
            )
            append_trade_log(entry_line)
            git_commit_and_push(f"mirage daemon exit {symbol} {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")


def log_externally_closed_positions(known_open, current_positions):
    """Detect and log positions that disappeared between cycles WITHOUT
    going through manage_positions()'s explicit close_position() call --
    almost always a standing stop order filling directly on Alpaca's
    side, independent of this loop. Confirmed live 2026-07-31: 8 of 11
    real exits that day were never logged because only the explicit-close
    path wrote to TRADE-LOG; a stop firing on its own left no record even
    though the account P&L was correct the whole time. Uses Alpaca's own
    fill ledger as the source of truth for entry/exit price and P&L,
    same approach used for the manual corrections earlier in this file's
    history."""
    current_symbols = {p["symbol"] for p in current_positions}
    disappeared = known_open - current_symbols
    for symbol in disappeared:
        fills = get_fills_today(symbol)
        if not fills:
            log(f"{symbol} disappeared from positions but no fills found today — "
                f"can't log a reason, flagging for manual review")
            continue
        buys = [(float(f["qty"]), float(f["price"])) for f in fills if f["side"] == "buy"]
        sells = [(float(f["qty"]), float(f["price"])) for f in fills if f["side"] == "sell"]
        buy_cost = sum(q * p for q, p in buys)
        sell_proceeds = sum(q * p for q, p in sells)
        buy_qty = sum(q for q, _ in buys)
        sell_qty = sum(q for q, _ in sells)
        if sell_qty <= 0:
            log(f"{symbol} disappeared from positions but no sell fill found today — "
                f"can't confirm it's actually closed, flagging for manual review")
            continue
        avg_entry = buy_cost / buy_qty if buy_qty else 0
        avg_exit = sell_proceeds / sell_qty
        pnl = sell_proceeds - buy_cost
        pnl_pct = (pnl / buy_cost * 100) if buy_cost else 0
        now = datetime.now(timezone.utc)
        entry_line = (
            f"<!-- DAEMON_EXIT: {symbol} {now.strftime('%Y-%m-%d %H:%M')} -->\n"
            f"### {now.strftime('%b %d %H:%M UTC')} — Intraday Daemon Exit (external fill)\n"
            f"**{symbol}** closed @ ~${avg_exit:.4f} | entry ${avg_entry:.4f} | "
            f"realized P&L ${pnl:.2f} ({pnl_pct:.1f}%) | reason: stop-loss order filled "
            f"(detected via position disappearance, not an explicit daemon close — "
            f"P&L computed from Alpaca's fill ledger)"
        )
        log(f"Logging externally-closed position: {symbol}, P&L ${pnl:.2f}")
        append_trade_log(entry_line)
        git_commit_and_push(f"mirage daemon exit {symbol} (stop fill) {now.strftime('%Y-%m-%d %H:%M')} UTC")


def screen_new_entry(equity, attempted, open_count):
    if open_count >= MAX_POSITIONS:
        return
    # top=50, not 10: the top ~10 gainers/losers are dominated by extreme
    # penny-stock/warrant moves (40-100%+) that fail GAP_MAX_PCT anyway --
    # confirmed live 2026-07-28/29, legitimate 3-20% candidates in real,
    # liquid names (e.g. LAD, GRMN, EXLS, NEO) sit just below the top 10
    # and were being missed entirely.
    candidates = get_movers(50) + get_most_actives(50)
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
        if abs(pct_change) < GAP_MIN_PCT or abs(pct_change) > GAP_MAX_PCT:
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
        # Tighter of the two candidates = closer to entry = smaller loss.
        # For a long, that's the HIGHER price (max), not the lower one.
        stop_price = max(or_low, entry_price * (1 - STOP_PCT))
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
        attempted.add(symbol)  # mark attempted even if the stop-placement below has trouble
        filled_qty, filled_avg_price = wait_for_fill(order["id"])
        if filled_qty <= 0:
            log(f"{symbol} buy did not confirm filled — SKIPPING stop placement, "
                f"will be caught by manage_positions/EOD-close but flag this run for review")
        else:
            # Recompute stop/target from the ACTUAL fill price, not the
            # pre-fill quote -- a thin/fast-moving stock can slip badly
            # (see wait_for_fill docstring). Falls back to the quoted
            # entry_price only if Alpaca didn't report a fill price.
            real_entry = filled_avg_price if filled_avg_price > 0 else entry_price
            slippage_pct = (real_entry - entry_price) / entry_price * 100 if entry_price else 0
            if abs(slippage_pct) > 2:
                log(f"{symbol} SLIPPAGE WARNING: quoted ${entry_price:.4f}, filled ${real_entry:.4f} "
                    f"({slippage_pct:+.1f}%) -- recomputing stop/target from real fill price")
            entry_price = real_entry
            stop_price = max(or_low, entry_price * (1 - STOP_PCT))
            target_price = entry_price + MIN_RR * (entry_price - stop_price)
            stop_order = place_order({
                "symbol": symbol, "qty": str(filled_qty), "side": "sell",
                "type": "stop", "stop_price": f"{stop_price:.2f}", "time_in_force": "day",
            })
            if not stop_order:
                log(f"{symbol} STOP PLACEMENT FAILED after fill confirmed — "
                    f"position is unprotected until next manage_positions cycle")
        risk = qty * abs(entry_price - stop_price)
        now = datetime.now(timezone.utc)
        entry_line = (
            f"<!-- DAEMON_ENTRY: {symbol} long {now.strftime('%Y-%m-%d')} -->\n"
            f"### {now.strftime('%b %d %H:%M UTC')} — Intraday Daemon Entry\n"
            f"**{symbol}** long {qty} sh @ ~${entry_price:.2f} (actual fill) | stop ${stop_price:.2f} | "
            f"target ${target_price:.2f} ({MIN_RR}:1) | gap {pct_change:.1f}%, ORB confirmed above ${or_high:.2f} | "
            f"Rule 1: {qty} x ${abs(entry_price - stop_price):.2f} = ${risk:.2f} "
            f"({risk / equity:.1%} of ${equity:,.0f} equity, cap {MAX_LOSS_PCT:.0%})"
        )
        append_trade_log(entry_line)
        git_commit_and_push(f"mirage daemon entry {symbol} {now.strftime('%Y-%m-%d %H:%M')} UTC")
        return  # one new entry per loop iteration is plenty; re-evaluate next cycle


def main():
    log("Mirage intraday daemon starting")
    if not past(START_UTC):
        log(f"before market hours (before {START_UTC[0]:02d}:{START_UTC[1]:02d} UTC) — "
            f"exiting immediately, not spinning until open. This run was likely a "
            f"manual/misfired trigger; the scheduled cron fires at market open.")
        return
    attempted = already_attempted_today()
    log(f"already-attempted symbols recovered from TRADE-LOG: {attempted or 'none'}")
    known_open = {p["symbol"] for p in get_positions()}
    log(f"positions open at daemon start: {known_open or 'none'}")
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
        log_externally_closed_positions(known_open, positions)
        manage_positions(equity)
        if not past(STOP_NEW_ENTRIES_AFTER_UTC):
            screen_new_entry(equity, attempted, len(positions))
        else:
            log("past new-entry cutoff (2:15pm Chicago) — management only, no new entries")
        known_open = {p["symbol"] for p in get_positions()}
        time.sleep(POLL_SECONDS)
    log("daemon loop ended; mandatory EOD-close routine remains the backstop at 2:45pm Chicago")


if __name__ == "__main__":
    sys.exit(main())
