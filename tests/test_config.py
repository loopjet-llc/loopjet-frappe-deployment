from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
	path = ROOT / "scripts" / name
	spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
	module = importlib.util.module_from_spec(spec)
	assert spec.loader
	spec.loader.exec_module(module)
	return module


class ConfigurationTest(unittest.TestCase):
	def test_generated_apps_match_lock(self):
		module = load_script("generate-apps.py")
		apps = module.generate()
		lock = json.loads((ROOT / "config" / "versions.json").read_text())
		self.assertEqual(len(apps), len(lock["apps"]))
		self.assertEqual([app["branch"] for app in apps], [app["ref"] for app in lock["apps"]])
		upstream_apps = module.generate(upstream=True)
		self.assertEqual(upstream_apps[0]["url"], "https://github.com/frappe/erpnext.git")
		self.assertEqual(
			upstream_apps[-1]["url"], "https://github.com/loopjet-llc/loopjet-frappe-custom.git"
		)

	def test_version_sorting(self):
		module = load_script("check-upstream-updates.py")
		versions = ["v16.9.2", "v16.10.0", "v16.9.12"]
		self.assertEqual(max(versions, key=module.version_key), "v16.10.0")


if __name__ == "__main__":
	unittest.main()
