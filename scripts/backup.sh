#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
set -a
# shellcheck disable=SC1090
source "${ENV_FILE:-.env}"
set +a

MODE=${STACK_MODE:-production}
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
destination=${BACKUP_DIR:-$ROOT/backups}/$timestamp
mkdir -p "$destination"

for site in "$ERP_SITE" "$CRM_SITE" "$HELPDESK_SITE"; do
  ./scripts/stack.sh "$MODE" exec -T backend bench --site "$site" backup --with-files --compress
  mkdir -p "$destination/$site"
  ./scripts/stack.sh "$MODE" cp "backend:/home/frappe/frappe-bench/sites/$site/private/backups/." "$destination/$site/"
done

find "${BACKUP_DIR:-$ROOT/backups}" -mindepth 1 -maxdepth 1 -type d \
  -mtime "+${BACKUP_RETENTION_DAYS:-14}" -exec rm -rf {} +

echo "Backup completed: $destination"
