#!/usr/bin/env python3
"""Validate local configuration without requiring Docker or network access."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r"^v\d+(?:\.\d+){1,3}(?:[-+][A-Za-z0-9.-]+)?$")


def main() -> None:
	data = json.loads((ROOT / "config" / "versions.json").read_text())
	assert data["schema"] == 1
	assert TAG.match(data["frappe_docker"]["ref"])
	assert TAG.match(data["frappe"]["ref"])
	names = [app["name"] for app in data["apps"]]
	assert len(names) == len(set(names))
	assert names == [
		"erpnext",
		"hrms",
		"crm",
		"telephony",
		"helpdesk",
		"raven",
		"loopjet_frappe_custom",
	]
	for app in data["apps"]:
		assert TAG.match(app["ref"]), app
		assert re.match(r"^[\w.-]+/[\w.-]+$", app["repository"]), app
	print("configuration valid")


if __name__ == "__main__":
	main()
