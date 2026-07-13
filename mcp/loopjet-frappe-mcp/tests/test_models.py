import pytest
from pydantic import ValidationError

from loopjet_frappe_mcp.models import DraftInvoiceInput, InvoiceItem, validate_optional_period
from loopjet_frappe_mcp.server import get_invoice_pdf_url


def test_service_period_allows_neither_date() -> None:
    validate_optional_period(None, None)


def test_service_period_requires_both_dates() -> None:
    with pytest.raises(ValueError):
        validate_optional_period("2026-07-01", None)
    with pytest.raises(ValueError):
        validate_optional_period(None, "2026-07-31")


def test_invoice_payload_maps_reverse_charge_and_optional_period() -> None:
    invoice = DraftInvoiceInput(
        customer="Studeez GmbH",
        service_period_start="2026-07-01",
        service_period_end="2026-07-31",
        reverse_charge_applies=True,
        items=[InvoiceItem(item_code="SERVICE", qty=1, rate=100)],
    )

    payload = invoice.to_frappe_doc()

    assert payload["docstatus"] if "docstatus" in payload else 0 == 0
    assert payload["reverse_charge_applies"] == 1
    assert payload["taxes"] == []
    assert payload["service_period_start"] == "2026-07-01"
    assert payload["service_period_end"] == "2026-07-31"


def test_invoice_model_rejects_partial_service_period() -> None:
    with pytest.raises(ValidationError):
        DraftInvoiceInput(
            customer="Studeez GmbH",
            service_period_start="2026-07-01",
            items=[InvoiceItem(item_code="SERVICE", qty=1, rate=100)],
        )


@pytest.mark.asyncio
async def test_pdf_url_is_encoded() -> None:
    result = await get_invoice_pdf_url("ACC/SINV 1", "Loopjet Invoice")

    assert "doctype=Sales+Invoice" in result["url"]
    assert "name=ACC%2FSINV+1" in result["url"]
    assert "format=Loopjet+Invoice" in result["url"]
