#!/usr/bin/env python3
"""Apply the minimal reviewed overlay to a pinned Frappe Docker checkout."""

from __future__ import annotations

import argparse
from pathlib import Path


NEEDLE = "    && chmod 644 /templates/nginx/frappe.conf.template\n"
ADDITION = "\nARG NODE_OPTIONS=--max-old-space-size=4096\nENV NODE_OPTIONS=${NODE_OPTIONS}\n"


ASSET_LINK = """echo "Linking fresh assets to volume..."
rm -rf "$ASSETS_PATH"
mkdir -p "$(dirname "$ASSETS_PATH")"
ln -s "$BAKED_PATH" "$ASSETS_PATH"
"""
SERIAL_ASSET_LINK = """# Each container shares the sites volume, but has its own baked assets.
sites_dir="$(dirname "$ASSETS_PATH")"
mkdir -p "$sites_dir"
(
    flock -x 9
    if [ ! -L "$ASSETS_PATH" ] || [ "$(readlink "$ASSETS_PATH")" != "$BAKED_PATH" ]; then
        echo "Linking fresh assets to volume..."
        rm -rf -- "$ASSETS_PATH"
        ln -s -- "$BAKED_PATH" "$ASSETS_PATH"
    fi
) 9>"$sites_dir/.loopjet-assets-link.lock"
"""


def replace_once(path: Path, needle: str, replacement: str) -> None:
	content = path.read_text()
	if replacement in content:
		return
	if content.count(needle) != 1:
		raise RuntimeError(f"Pinned Frappe Docker file no longer matches the reviewed overlay: {path}")
	path.write_text(content.replace(needle, replacement))


def apply_overlay(root: Path) -> None:
	replace_once(root / "images" / "custom" / "Containerfile", NEEDLE, NEEDLE + ADDITION)
	replace_once(
		root / "resources" / "core" / "main-entrypoint.sh",
		ASSET_LINK,
		SERIAL_ASSET_LINK,
	)

def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("root", type=Path)
	args = parser.parse_args()
	apply_overlay(args.root)


if __name__ == "__main__":
	main()
