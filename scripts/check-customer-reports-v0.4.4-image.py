"""Run inside the candidate image, without network access or production mounts."""
from pathlib import Path

import loopjet_frappe_custom
from loopjet_frappe_custom.customer_reports import is_customer_report_pdf

assert loopjet_frappe_custom.__version__ == "0.4.4"
assert is_customer_report_pdf("/private/files/august-2026.pdf")
assert not is_customer_report_pdf("/private/files/august-2026.docx")

app_root = Path("/home/frappe/frappe-bench/apps/loopjet_frappe_custom/loopjet_frappe_custom")
download_source = (app_root / "customer_reports.py").read_text()
report_script = (
	app_root
	/ "loopjet_custom"
	/ "doctype"
	/ "loopjet_customer_report"
	/ "loopjet_customer_report.js"
).read_text()
assert "def download_customer_report" in download_source
assert 'report.check_permission("read")' in download_source
assert "file_path.read_bytes()" in download_source
assert 'response.type = "download"' in download_source
assert "loopjet_frappe_custom.customer_reports.download_customer_report" in report_script
print("customer reports raw download passed")
