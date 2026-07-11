#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
set -a
# shellcheck disable=SC1090
source "${ENV_FILE:-.env}"
set +a

MODE=${STACK_MODE:-production}
[[ "$MODE" == production || "$MODE" == hostinger ]] || {
  echo "Upgrade is restricted to production or Hostinger mode." >&2
  exit 2
}

./scripts/backup.sh
./scripts/stack.sh "$MODE" pull
./scripts/stack.sh "$MODE" up -d --remove-orphans

for site in "$ERP_SITE" "$CRM_SITE" "$HELPDESK_SITE"; do
  ./scripts/stack.sh "$MODE" exec -T backend bench --site "$site" set-maintenance-mode on
  ./scripts/stack.sh "$MODE" exec -T backend bench --site "$site" migrate
  ./scripts/stack.sh "$MODE" exec -T backend bench --site "$site" clear-cache
  ./scripts/stack.sh "$MODE" exec -T backend bench --site "$site" set-maintenance-mode off
done

./scripts/healthcheck.sh
echo "Upgrade completed. Retain the pre-upgrade backup until business validation is complete."
