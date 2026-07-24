#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

# shellcheck disable=SC1091
[[ -f .env ]] && set -a && source .env && set +a
CUSTOM_IMAGE=${CUSTOM_IMAGE:-ghcr.io/loopjet-llc/loopjet-frappe-suite}
CUSTOM_TAG=${CUSTOM_TAG:-local}
BUILD_PLATFORM=${BUILD_PLATFORM:-linux/amd64}
SOURCE_MODE=${SOURCE_MODE:-upstream}

RUNTIME=$(./scripts/bootstrap-frappe-docker.sh)
generate_args=()
FRAPPE_PATH=https://github.com/loopjet-llc/loopjet-frappe.git
if [[ "$SOURCE_MODE" == upstream ]]; then
  generate_args+=(--upstream)
  FRAPPE_PATH=https://github.com/frappe/frappe.git
elif [[ "$SOURCE_MODE" != mirror ]]; then
  echo "SOURCE_MODE must be 'mirror' or 'upstream'." >&2
  exit 2
fi
./scripts/generate-apps.py "${generate_args[@]}"
FRAPPE_REF=$(python3 -c 'import json; print(json.load(open("config/versions.json"))["frappe"]["ref"])')
APPS_CACHE_BUST=$(python3 -c 'import hashlib; print(hashlib.sha256(open("config/apps.generated.json", "rb").read()).hexdigest())')

build_flags=()
if [[ "${NO_CACHE:-0}" == "1" || "${NO_CACHE:-false}" == "true" ]]; then
  build_flags+=(--no-cache)
fi

docker build \
  "${build_flags[@]}" \
  --platform "$BUILD_PLATFORM" \
  --build-arg "FRAPPE_PATH=$FRAPPE_PATH" \
  --build-arg "FRAPPE_BRANCH=$FRAPPE_REF" \
  --build-arg "CACHE_BUST=$APPS_CACHE_BUST" \
  --secret "id=apps_json,src=$ROOT/config/apps.generated.json" \
  --tag "$CUSTOM_IMAGE:$CUSTOM_TAG" \
  --file "$RUNTIME/images/custom/Containerfile" \
  "$RUNTIME"

printf 'Built %s:%s\n' "$CUSTOM_IMAGE" "$CUSTOM_TAG"
