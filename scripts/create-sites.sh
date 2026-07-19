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
ERP_COMPANY=${ERP_COMPANY:-Loopjet LLC}
CRM_CREATE_CUSTOMER_DEAL_STATUS=${CRM_CREATE_CUSTOMER_DEAL_STATUS:-Won}

site_exists() {
  ./scripts/stack.sh "$MODE" exec -T backend test -e "sites/$1"
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
install_app "$ERP_SITE" crm
install_app "$ERP_SITE" helpdesk
install_app "$ERP_SITE" raven
install_app "$ERP_SITE" loopjet_frappe_custom

ensure_alias() {
  local alias=$1
  [[ "$alias" == "$ERP_SITE" ]] && return

  if ./scripts/stack.sh "$MODE" exec -T backend test -d "sites/$alias" && \
     ! ./scripts/stack.sh "$MODE" exec -T backend test -L "sites/$alias"; then
    echo "Refusing to replace existing standalone site $alias. Back it up and move it aside first." >&2
    exit 2
  fi

  ./scripts/stack.sh "$MODE" exec -T backend bench setup add-domain "$alias" --site "$ERP_SITE"
  ./scripts/stack.sh "$MODE" exec -T backend ln -sfn "$ERP_SITE" "sites/$alias"
}

ensure_alias "$CRM_SITE"
ensure_alias "$HELPDESK_SITE"

./scripts/stack.sh "$MODE" exec -T backend bench --site "$ERP_SITE" migrate
./scripts/stack.sh "$MODE" exec -T backend bench --site "$ERP_SITE" enable-scheduler
./scripts/stack.sh "$MODE" exec -T backend bench --site "$ERP_SITE" execute \
  "frappe.get_doc(\"ERPNext CRM Settings\").update({\"enabled\": 1, \"erpnext_company\": \"$ERP_COMPANY\", \"is_erpnext_in_different_site\": 0, \"create_customer_on_status_change\": 1, \"deal_status\": \"$CRM_CREATE_CUSTOMER_DEAL_STATUS\"}).save"
./scripts/stack.sh "$MODE" exec -T backend bench --site "$ERP_SITE" execute \
  "frappe.get_doc(\"ERPNext HD Settings\").update({\"enabled\": 1}).save"
./scripts/stack.sh "$MODE" exec -T backend bench --site "$ERP_SITE" clear-cache

echo "Loopjet connected Frappe site is ready. $CRM_SITE and $HELPDESK_SITE are aliases of $ERP_SITE."
