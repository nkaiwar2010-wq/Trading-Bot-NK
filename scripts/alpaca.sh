#!/usr/bin/env bash
# Alpaca API wrapper. All trading API calls go through here.
# Usage: bash scripts/alpaca.sh <command> [args...]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

: "${ALPACA_API_KEY:?ALPACA_API_KEY not set in environment}"
: "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set in environment}"

API="${ALPACA_ENDPOINT:-https://paper-api.alpaca.markets/v2}"
DATA="${ALPACA_DATA_ENDPOINT:-https://data.alpaca.markets/v2}"
DATA_ROOT="${DATA%/v2}"
H_KEY="APCA-API-KEY-ID: $ALPACA_API_KEY"
H_SEC="APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY"

cmd="${1:-}"
shift || true

case "$cmd" in
  account)
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/account"
    ;;
  positions)
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/positions"
    ;;
  position)
    sym="${1:?usage: position SYM}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/positions/$sym"
    ;;
  quote)
    sym="${1:?usage: quote SYM}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$DATA/stocks/$sym/quotes/latest"
    ;;
  orders)
    status="${1:-open}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/orders?status=$status"
    ;;
  order)
    body="${1:?usage: order '<json>'}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" -H "Content-Type: application/json" \
      -X POST -d "$body" "$API/orders"
    ;;
  cancel)
    oid="${1:?usage: cancel ORDER_ID}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/orders/$oid"
    ;;
  cancel-all)
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/orders"
    ;;
  close)
    sym="${1:?usage: close SYM}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/positions/$sym"
    ;;
  close-all)
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/positions"
    ;;
  options-chain)
    # usage: options-chain SYM [call|put] [YYYY-MM-DD]
    sym="${1:?usage: options-chain SYM [call|put] [YYYY-MM-DD]}"
    type="${2:-}"
    exp="${3:-}"
    qs=""
    [[ -n "$type" ]] && qs="${qs}&type=${type}"
    [[ -n "$exp" ]] && qs="${qs}&expiration_date=${exp}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$DATA_ROOT/v1beta1/options/snapshots/$sym?limit=100${qs}"
    ;;
  option-quote)
    # usage: option-quote OCC_SYMBOL
    sym="${1:?usage: option-quote OCC_SYMBOL}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$DATA_ROOT/v1beta1/options/quotes/latest?symbols=$sym"
    ;;
  movers)
    # usage: movers [top_n]  (gainers+losers, real-time SIP, resets at market open)
    top="${1:-10}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$DATA_ROOT/v1beta1/screener/stocks/movers?top=$top"
    ;;
  most-actives)
    # usage: most-actives [top_n] [volume|trades]
    top="${1:-10}"
    by="${2:-volume}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$DATA_ROOT/v1beta1/screener/stocks/most-actives?top=$top&by=$by"
    ;;
  bars)
    # usage: bars SYM [timeframe] [limit]  (e.g. bars AAPL 5Min 20)
    sym="${1:?usage: bars SYM [timeframe] [limit]}"
    tf="${2:-5Min}"
    limit="${3:-30}"
    start="$(date -u +%Y-%m-%d)T00:00:00Z"
    curl -fsS -H "$H_KEY" -H "$H_SEC" \
      "$DATA/stocks/$sym/bars?timeframe=$tf&start=$start&limit=$limit&adjustment=raw&feed=iex"
    ;;
  *)
    echo "Usage: bash scripts/alpaca.sh <account|positions|position|quote|orders|order|cancel|cancel-all|close|close-all|options-chain|option-quote|movers|most-actives|bars> [args]" >&2
    exit 1
    ;;
esac
echo
