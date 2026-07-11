#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

MODE=${1:-local}
shift || true
RUNTIME=$(./scripts/bootstrap-frappe-docker.sh)

files=(
  -f "$RUNTIME/compose.yaml"
  -f "$RUNTIME/overrides/compose.mariadb.yaml"
  -f "$RUNTIME/overrides/compose.redis.yaml"
  -f "$ROOT/compose/loopjet.yaml"
)

case "$MODE" in
  local) files+=(-f "$RUNTIME/overrides/compose.noproxy.yaml") ;;
  production) files+=(-f "$RUNTIME/overrides/compose.https.yaml") ;;
  hostinger) files+=(-f "$ROOT/compose/hostinger-traefik.yaml") ;;
  *) echo "Usage: $0 {local|production|hostinger} [docker compose arguments...]" >&2; exit 2 ;;
esac

exec docker compose --project-name loopjet-frappe --env-file "${ENV_FILE:-$ROOT/.env}" "${files[@]}" "$@"
