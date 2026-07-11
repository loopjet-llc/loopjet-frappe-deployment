#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
[[ -f .env ]] || { echo "Copy .env.example to .env first." >&2; exit 2; }
set -a
# shellcheck disable=SC1091
source .env
set +a

MODE=${STACK_MODE:-local}

site_exists() {
  ./scripts/stack.sh "$MODE" exec -T backend test -d "sites/$1"
}

create_site() {
  local site=$1
  if site_exists "$site"; then
    echo "Site $site already exists."
    return
  fi
  ./scripts/stack.sh "$MODE" exec -T backend bench new-site "$site" \
    --db-type mariadb \
    --mariadb-root-password "$DB_PASSWORD" \
    --admin-password "$ADMIN_PASSWORD" \
    --no-mariadb-socket
}

install_app() {
  local site=$1 app=$2
  if ./scripts/stack.sh "$MODE" exec -T backend bench --site "$site" list-apps | grep -Fxq "$app"; then
    echo "$app is already installed on $site."
  else
    ./scripts/stack.sh "$MODE" exec -T backend bench --site "$site" install-app "$app"
  fi
}

create_site "$ERP_SITE"
install_app "$ERP_SITE" erpnext
install_app "$ERP_SITE" hrms
install_app "$ERP_SITE" loopjet_frappe_custom

create_site "$CRM_SITE"
install_app "$CRM_SITE" crm
install_app "$CRM_SITE" loopjet_frappe_custom

create_site "$HELPDESK_SITE"
install_app "$HELPDESK_SITE" helpdesk
install_app "$HELPDESK_SITE" loopjet_frappe_custom

for site in "$ERP_SITE" "$CRM_SITE" "$HELPDESK_SITE"; do
  ./scripts/stack.sh "$MODE" exec -T backend bench --site "$site" migrate
done

echo "All Loopjet sites are ready."
