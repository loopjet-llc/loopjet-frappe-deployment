#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

# shellcheck disable=SC1091
[[ -f .env ]] && set -a && source .env && set +a
CUSTOM_IMAGE=${CUSTOM_IMAGE:-ghcr.io/loopjet-llc/loopjet-frappe-suite}
CUSTOM_TAG=${CUSTOM_TAG:-local}
BUILD_PLATFORM=${BUILD_PLATFORM:-linux/amd64}

RUNTIME=$(./scripts/bootstrap-frappe-docker.sh)
./scripts/generate-apps.py
FRAPPE_REF=$(python3 -c 'import json; print(json.load(open("config/versions.json"))["frappe"]["ref"])')

docker build \
  --platform "$BUILD_PLATFORM" \
  --build-arg "FRAPPE_PATH=https://github.com/loopjet-llc/loopjet-frappe.git" \
  --build-arg "FRAPPE_BRANCH=$FRAPPE_REF" \
  --secret "id=apps_json,src=$ROOT/config/apps.generated.json" \
  --tag "$CUSTOM_IMAGE:$CUSTOM_TAG" \
  --file "$RUNTIME/images/custom/Containerfile" \
  "$RUNTIME"

printf 'Built %s:%s\n' "$CUSTOM_IMAGE" "$CUSTOM_TAG"
