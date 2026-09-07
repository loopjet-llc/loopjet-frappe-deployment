"""Run inside the candidate image, without network access or production mounts."""
import json
from pathlib import Path
from types import SimpleNamespace

import loopjet_frappe_custom
from loopjet_frappe_custom.customer_reports import (
	CUSTOMER_REPORT_DOCTYPE,
	is_customer_report_pdf,
	make_customer_report_file_private,
)
from loopjet_frappe_custom.workspace import (
	CUSTOMER_REPORTS_SHORTCUT_LABEL,
	add_customer_reports_shortcut_to_layout,
)

assert loopjet_frappe_custom.__version__ == "0.4.3"
assert is_customer_report_pdf("/private/files/august-2026.pdf")
assert not is_customer_report_pdf("/private/files/august-2026.docx")

report_file = SimpleNamespace(attached_to_doctype=CUSTOMER_REPORT_DOCTYPE, is_private=0)
assert make_customer_report_file_private(report_file).is_private == 1

app_root = Path("/home/frappe/frappe-bench/apps/loopjet_frappe_custom/loopjet_frappe_custom")
doctype = json.loads(
	(
		app_root
		/ "loopjet_custom"
		/ "doctype"
		/ "loopjet_customer_report"
		/ "loopjet_customer_report.json"
	).read_text()
)
fields = {field["fieldname"]: field for field in doctype["fields"]}
assert doctype["name"] == CUSTOMER_REPORT_DOCTYPE
assert fields["customer"]["options"] == "Customer"
assert fields["report_file"]["fieldtype"] == "Attach"
assert {permission["role"] for permission in doctype["permissions"]} == {
	"Projects Manager",
	"System Manager",
}

layout, changed = add_customer_reports_shortcut_to_layout("[]")
assert changed is True
assert CUSTOMER_REPORTS_SHORTCUT_LABEL in layout
assert add_customer_reports_shortcut_to_layout(layout)[1] is False

hooks = (app_root / "hooks.py").read_text()
assert "make_customer_report_file_private" in hooks
assert "public/js/customer.js" in hooks
assert "PDF herunterladen" in (
	app_root
	/ "loopjet_custom"
	/ "doctype"
	/ "loopjet_customer_report"
	/ "loopjet_customer_report.js"
).read_text()
print(json.dumps({"version": loopjet_frappe_custom.__version__, "customer_reports": "passed"}))
