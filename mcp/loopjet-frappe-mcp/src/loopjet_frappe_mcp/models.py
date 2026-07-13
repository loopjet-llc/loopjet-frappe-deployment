from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class InvoiceItem(BaseModel):
    item_code: str = Field(description="ERPNext item code")
    description: str | None = Field(default=None, description="Optional line description")
    qty: float = Field(default=1, gt=0)
    rate: float = Field(ge=0)
    uom: str = "Unit"
    income_account: str | None = None
    cost_center: str | None = None


class DraftInvoiceInput(BaseModel):
    customer: str
    items: list[InvoiceItem] = Field(min_length=1)
    company: str = "Loopjet LLC"
    currency: str = "EUR"
    posting_date: str | None = Field(default=None, description="YYYY-MM-DD; defaults in Frappe")
    due_date: str | None = Field(default=None, description="YYYY-MM-DD")
    service_period_start: str | None = Field(default=None, description="Optional YYYY-MM-DD")
    service_period_end: str | None = Field(default=None, description="Optional YYYY-MM-DD")
    reverse_charge_applies: bool = False
    document_language: str = Field(default="English", description="English or Deutsch")
    debit_to: str = "Debtors - LJ"
    cost_center: str = "Main - LJ"
    income_account: str = "Sales - LJ"
    selling_price_list: str = "Standard Selling EUR"
    remarks: str | None = None

    @model_validator(mode="after")
    def validate_service_period(self) -> DraftInvoiceInput:
        validate_optional_period(self.service_period_start, self.service_period_end)
        return self

    def to_frappe_doc(self) -> dict[str, Any]:
        doc: dict[str, Any] = {
            "doctype": "Sales Invoice",
            "company": self.company,
            "customer": self.customer,
            "currency": self.currency,
            "conversion_rate": 1,
            "selling_price_list": self.selling_price_list,
            "price_list_currency": self.currency,
            "plc_conversion_rate": 1,
            "debit_to": self.debit_to,
            "cost_center": self.cost_center,
            "loopjet_document_language": self.document_language,
            "reverse_charge_applies": 1 if self.reverse_charge_applies else 0,
            "items": [
                {
                    "item_code": item.item_code,
                    "description": item.description,
                    "qty": item.qty,
                    "uom": item.uom,
                    "rate": item.rate,
                    "income_account": item.income_account or self.income_account,
                    "cost_center": item.cost_center or self.cost_center,
                }
                for item in self.items
            ],
        }
        if self.posting_date:
            doc["posting_date"] = self.posting_date
        if self.due_date:
            doc["due_date"] = self.due_date
        if self.service_period_start:
            doc["service_period_start"] = self.service_period_start
        if self.service_period_end:
            doc["service_period_end"] = self.service_period_end
        if self.remarks:
            doc["remarks"] = self.remarks
        if self.reverse_charge_applies:
            doc["taxes"] = []
        return doc


class DraftInvoiceUpdate(BaseModel):
    customer: str | None = None
    currency: str | None = None
    posting_date: str | None = None
    due_date: str | None = None
    service_period_start: str | None = None
    service_period_end: str | None = None
    reverse_charge_applies: bool | None = None
    document_language: str | None = None
    remarks: str | None = None
    items: list[InvoiceItem] | None = None


class TicketInput(BaseModel):
    subject: str
    description: str
    raised_by: str | None = None
    priority: str = "Medium"


def validate_optional_period(start: str | None, end: str | None) -> None:
    if bool(start) ^ bool(end):
        raise ValueError("Provide both service_period_start and service_period_end, or neither.")
