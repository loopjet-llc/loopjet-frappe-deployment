#!/usr/bin/env python3
"""Apply the minimal reviewed overlay to a pinned Frappe Docker checkout."""

from __future__ import annotations

import argparse
from pathlib import Path


NEEDLE = "    && chmod 644 /templates/nginx/frappe.conf.template\n"
ADDITION = "\nARG NODE_OPTIONS=--max-old-space-size=4096\nENV NODE_OPTIONS=${NODE_OPTIONS}\n"


def apply_overlay(root: Path) -> None:
	containerfile = root / "images" / "custom" / "Containerfile"
	content = containerfile.read_text()
	if ADDITION.strip() in content:
		return
	if content.count(NEEDLE) != 1:
		raise RuntimeError("Pinned Frappe Docker Containerfile no longer matches the reviewed overlay")
	containerfile.write_text(content.replace(NEEDLE, NEEDLE + ADDITION))


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("root", type=Path)
	args = parser.parse_args()
	apply_overlay(args.root)


if __name__ == "__main__":
	main()
