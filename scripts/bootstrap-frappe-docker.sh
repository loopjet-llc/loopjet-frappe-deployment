#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
RUNTIME="$ROOT/.runtime/frappe_docker"
REF=$(python3 -c 'import json; print(json.load(open("config/versions.json"))["frappe_docker"]["ref"])' 2>/dev/null || \
  python3 -c "import json; print(json.load(open('$ROOT/config/versions.json'))['frappe_docker']['ref'])")

if [[ -d "$RUNTIME/.git" ]]; then
  git -C "$RUNTIME" fetch --tags origin
else
  mkdir -p "$(dirname "$RUNTIME")"
  git clone https://github.com/frappe/frappe_docker.git "$RUNTIME"
fi

git -C "$RUNTIME" checkout --detach "$REF" >&2
git -C "$RUNTIME" reset --hard "$REF" >&2
python3 "$ROOT/scripts/apply-frappe-docker-overlay.py" "$RUNTIME"
printf '%s\n' "$RUNTIME"
