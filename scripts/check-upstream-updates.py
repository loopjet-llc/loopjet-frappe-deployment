#!/usr/bin/env python3
"""Find or apply latest compatible upstream release tags."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ROOT / "config" / "versions.json"


def version_key(tag: str) -> tuple[int, ...]:
	numbers = re.findall(r"\d+", tag)
	return tuple(int(value) for value in numbers)


def github_json(path: str) -> object:
	request = urllib.request.Request(
		f"https://api.github.com{path}",
		headers={
			"Accept": "application/vnd.github+json",
			"User-Agent": "loopjet-release-checker",
			**(
				{"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
				if os.environ.get("GITHUB_TOKEN")
				else {}
			),
		},
	)
	with urllib.request.urlopen(request, timeout=30) as response:
		return json.load(response)


def latest_tag(repository: str, current: str) -> str:
	major = current.split(".", 1)[0]
	tags = github_json(f"/repos/{repository}/tags?per_page=100")
	candidates = [tag["name"] for tag in tags if tag["name"].split(".", 1)[0] == major]
	if not candidates:
		raise RuntimeError(f"No compatible {major}.x tags found for {repository}")
	return max(candidates, key=version_key)


def update_lock(apply: bool = False) -> list[tuple[str, str, str]]:
	data = json.loads(VERSIONS.read_text())
	targets = [data["frappe_docker"], data["frappe"]]
	targets.extend(app for app in data["apps"] if app.get("track", True))
	changes = []
	for target in targets:
		repository = target.get("upstream", target["repository"])
		new_ref = latest_tag(repository, target["ref"])
		if new_ref != target["ref"]:
			changes.append((repository, target["ref"], new_ref))
			target["ref"] = new_ref
	if apply and changes:
		data["generated_at"] = date.today().isoformat()
		VERSIONS.write_text(json.dumps(data, indent=2) + "\n")
	return changes


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--update", action="store_true")
	args = parser.parse_args()
	changes = update_lock(args.update)
	for repository, old, new in changes:
		print(f"{repository}: {old} -> {new}")
	if not changes:
		print("All tracked releases are current.")


if __name__ == "__main__":
	main()
