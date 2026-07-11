#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 SITE DATABASE_BACKUP [PUBLIC_FILES] [PRIVATE_FILES]" >&2
  exit 2
fi

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
set -a
# shellcheck disable=SC1090
source "${ENV_FILE:-.env}"
set +a

site=$1
database=$2
public_files=${3:-}
private_files=${4:-}
MODE=${STACK_MODE:-production}

case "$site" in
  "$ERP_SITE"|"$CRM_SITE"|"$HELPDESK_SITE") ;;
  *) echo "Refusing to restore unknown site: $site" >&2; exit 2 ;;
esac

staging="/tmp/loopjet-restore-$RANDOM"
./scripts/stack.sh "$MODE" exec -T backend mkdir -p "$staging"
./scripts/stack.sh "$MODE" cp "$database" "backend:$staging/database.sql.gz"
args=(bench --site "$site" restore "$staging/database.sql.gz" --force)

if [[ -n "$public_files" ]]; then
  ./scripts/stack.sh "$MODE" cp "$public_files" "backend:$staging/public-files.tar"
  args+=(--with-public-files "$staging/public-files.tar")
fi
if [[ -n "$private_files" ]]; then
  ./scripts/stack.sh "$MODE" cp "$private_files" "backend:$staging/private-files.tar"
  args+=(--with-private-files "$staging/private-files.tar")
fi

./scripts/stack.sh "$MODE" exec -T backend "${args[@]}"
./scripts/stack.sh "$MODE" exec -T backend bench --site "$site" migrate
./scripts/stack.sh "$MODE" exec -T backend rm -rf "$staging"
echo "Restore completed for $site."
