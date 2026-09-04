"""Run inside the candidate image, without network access or production mounts."""
import hashlib
import json
import sys
from types import SimpleNamespace

import loopjet_frappe_custom
from loopjet_frappe_custom.invoice_print import INVOICE_CSS, INVOICE_HTML

assert loopjet_frappe_custom.__version__ == "0.4.2"
hashes = {
    "html": hashlib.sha256(INVOICE_HTML.encode()).hexdigest(),
    "css": hashlib.sha256(INVOICE_CSS.encode()).hexdigest(),
}
assert hashes == {
    "html": "9407deb405911b8e382dee068df807e9d5c7fddd90bb430a70f4351bfbe42b47",
    "css": "93273be1178dd3958951fd1caa78ea1d946bbfdf93195a91a45df6f6ad7c3d95",
}
sys.modules["frappe"] = SimpleNamespace(db=SimpleNamespace(exists=lambda *args: True))
from loopjet_frappe_custom import branding

documents = {name: SimpleNamespace() for name in branding.PRINT_FORMAT_NAME_BY_DOCTYPE.values()}
branding._get_or_new = lambda doctype, name: documents[name]
branding._save = lambda doc: None
branding._set_default_print_format = lambda *args: None
branding._disable_legacy_print_formats = lambda: None
for _ in range(2):
    branding.install_print_formats()
    assert documents["Loopjet Invoice"].html == INVOICE_HTML
    assert documents["Loopjet Invoice"].css == INVOICE_CSS
    assert documents["Loopjet Offer"].html == branding.PRINT_HTML
    assert documents["Loopjet Offer"].css == branding.PRINT_CSS
print(json.dumps({"version": loopjet_frappe_custom.__version__, "hashes": hashes, "reinstall": "passed"}))
