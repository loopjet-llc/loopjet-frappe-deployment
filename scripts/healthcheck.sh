#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
set -a
# shellcheck disable=SC1090
source "${ENV_FILE:-.env}"
set +a

SCHEME=${HEALTHCHECK_SCHEME:-http}
PORT=${HEALTHCHECK_PORT:-${HTTP_PUBLISH_PORT:-8080}}

for site in "$ERP_SITE" "$CRM_SITE" "$HELPDESK_SITE"; do
  url="$SCHEME://$site:$PORT/api/method/ping"
  response=$(curl --fail --silent --show-error --max-time 20 "$url")
  [[ "$response" == *'"pong"'* ]] || { echo "Unexpected response from $url: $response" >&2; exit 1; }
  echo "healthy: $site"
done
