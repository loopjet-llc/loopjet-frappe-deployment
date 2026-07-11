#!/usr/bin/env python3
"""Generate the Frappe Docker apps manifest from the reviewed version lock."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ROOT / "config" / "versions.json"
DEFAULT_OUTPUT = ROOT / "config" / "apps.generated.json"


def generate(version_file: Path = VERSIONS, upstream: bool = False) -> list[dict[str, str]]:
	data = json.loads(version_file.read_text())
	return [
		{
			"url": f"https://github.com/{app.get('upstream', app['repository']) if upstream else app['repository']}.git",
			"branch": app["ref"],
		}
		for app in data["apps"]
	]


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
	parser.add_argument("--upstream", action="store_true", help="Use official upstream repositories when available")
	args = parser.parse_args()
	args.output.parent.mkdir(parents=True, exist_ok=True)
	args.output.write_text(json.dumps(generate(upstream=args.upstream), indent=2) + "\n")
	print(args.output)


if __name__ == "__main__":
	main()
