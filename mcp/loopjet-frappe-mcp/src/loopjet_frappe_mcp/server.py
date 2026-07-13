from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import AnyHttpUrl

from loopjet_frappe_mcp.auth import FrappeTokenVerifier
from loopjet_frappe_mcp.config import settings
from loopjet_frappe_mcp.frappe import FrappeClient, FrappeError
from loopjet_frappe_mcp.models import (
    DraftInvoiceInput,
    DraftInvoiceUpdate,
    TicketInput,
    validate_optional_period,
)

mcp = FastMCP(
    "Loopjet Frappe",
    instructions=(
        "Operate on Loopjet ERPNext invoices and Helpdesk tickets. "
        "Access is always evaluated by Frappe using the current user's API token."
    ),
    host=settings.mcp_host,
    port=settings.mcp_port,
    json_response=True,
    stateless_http=True,
    token_verifier=FrappeTokenVerifier(),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(str(settings.mcp_issuer_url)),
        resource_server_url=AnyHttpUrl(str(settings.mcp_resource_server_url)),
        required_scopes=["frappe"],
    ),
)


def _client() -> FrappeClient:
    access_token = get_access_token()
    if access_token is None:
        raise ToolError("Missing Authorization: Bearer <frappe_api_key>:<frappe_api_secret>")
    return FrappeClient(str(settings.frappe_base_url), access_token.token)


async def _call(coro: Any) -> Any:
    try:
        return await coro
    except FrappeError as exc:
        raise ToolError(str(exc)) from exc
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool()
async def whoami() -> dict[str, str]:
    """Return the Frappe user represented by the current bearer token."""
    user = await _call(_client().get_logged_user())
    return {"user": user}


@mcp.tool()
async def list_customers(search: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    """List customers visible to the current Frappe user."""
    filters: list[list[Any]] = []
    if search:
        filters.append(["Customer", "customer_name", "like", f"%{search}%"])
    return await _call(
        _client().list_docs(
            "Customer",
            fields=["name", "customer_name", "customer_type", "default_currency", "modified"],
            filters=filters,
            limit=limit,
        )
    )


@mcp.tool()
async def get_customer(name: str) -> dict[str, Any]:
    """Get one customer by ERPNext customer name/id."""
    return await _call(_client().get_doc("Customer", name))


@mcp.tool()
async def list_invoices(
    customer: str | None = None,
    status: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List Sales Invoices visible to the current Frappe user."""
    filters: list[list[Any]] = []
    if customer:
        filters.append(["Sales Invoice", "customer", "=", customer])
    if status:
        filters.append(["Sales Invoice", "status", "=", status])
    return await _call(
        _client().list_docs(
            "Sales Invoice",
            fields=[
                "name",
                "customer",
                "customer_name",
                "posting_date",
                "due_date",
                "status",
                "docstatus",
                "currency",
                "grand_total",
                "outstanding_amount",
                "service_period_start",
                "service_period_end",
                "reverse_charge_applies",
                "modified",
            ],
            filters=filters,
            limit=limit,
        )
    )


@mcp.tool()
async def get_invoice(name: str) -> dict[str, Any]:
    """Get a Sales Invoice by name."""
    return await _call(_client().get_doc("Sales Invoice", name))


@mcp.tool()
async def create_draft_invoice(invoice: DraftInvoiceInput) -> dict[str, Any]:
    """Create a draft Sales Invoice. This never submits accounting entries."""
    return await _call(_client().create_doc("Sales Invoice", invoice.to_frappe_doc()))


@mcp.tool()
async def update_draft_invoice(name: str, updates: DraftInvoiceUpdate) -> dict[str, Any]:
    """Update a draft Sales Invoice. Submitted invoices are refused."""
    client = _client()
    existing = await _call(client.get_doc("Sales Invoice", name))
    if existing.get("docstatus") != 0:
        raise ToolError("Only draft invoices can be updated through MCP.")

    payload = updates.model_dump(exclude_none=True)
    start = payload.get("service_period_start", existing.get("service_period_start"))
    end = payload.get("service_period_end", existing.get("service_period_end"))
    validate_optional_period(start, end)
    if "document_language" in payload:
        payload["loopjet_document_language"] = payload.pop("document_language")
    if "reverse_charge_applies" in payload:
        payload["reverse_charge_applies"] = 1 if payload["reverse_charge_applies"] else 0
        if payload["reverse_charge_applies"]:
            payload["taxes"] = []
    if updates.items is not None:
        payload["items"] = [
            {
                "item_code": item.item_code,
                "description": item.description,
                "qty": item.qty,
                "uom": item.uom,
                "rate": item.rate,
                "income_account": item.income_account,
                "cost_center": item.cost_center,
            }
            for item in updates.items
        ]
    return await _call(client.update_doc("Sales Invoice", name, payload))


@mcp.tool()
async def get_invoice_pdf_url(name: str, print_format: str = "Loopjet Invoice") -> dict[str, str]:
    """Return an authenticated Frappe PDF download URL for a Sales Invoice."""
    base_url = str(settings.frappe_base_url).rstrip("/")
    query = urlencode(
        {
            "doctype": "Sales Invoice",
            "name": name,
            "format": print_format,
            "no_letterhead": 0,
        }
    )
    return {"url": f"{base_url}/api/method/frappe.utils.print_format.download_pdf?{query}"}


@mcp.tool()
async def list_tickets(
    status: str | None = None, raised_by: str | None = None, limit: int = 20
) -> list[dict[str, Any]]:
    """List Helpdesk tickets visible to the current Frappe user."""
    filters: list[list[Any]] = []
    if status:
        filters.append(["HD Ticket", "status", "=", status])
    if raised_by:
        filters.append(["HD Ticket", "raised_by", "=", raised_by])
    return await _call(
        _client().list_docs(
            "HD Ticket",
            fields=["name", "subject", "status", "priority", "raised_by", "modified"],
            filters=filters,
            limit=limit,
        )
    )


@mcp.tool()
async def get_ticket(name: str) -> dict[str, Any]:
    """Get a Helpdesk ticket by name."""
    return await _call(_client().get_doc("HD Ticket", name))


@mcp.tool()
async def create_ticket(ticket: TicketInput) -> dict[str, Any]:
    """Create a Helpdesk ticket as the current Frappe user."""
    doc = ticket.model_dump(exclude_none=True)
    doc["doctype"] = "HD Ticket"
    return await _call(_client().create_doc("HD Ticket", doc))


@mcp.tool()
async def update_ticket_status(name: str, status: str) -> dict[str, Any]:
    """Update a Helpdesk ticket status if the current user has permission."""
    return await _call(_client().update_doc("HD Ticket", name, {"status": status}))


@mcp.tool()
async def add_ticket_comment(name: str, comment: str) -> dict[str, Any]:
    """Add an internal Frappe comment to a Helpdesk ticket."""
    doc = {
        "doctype": "Comment",
        "comment_type": "Comment",
        "reference_doctype": "HD Ticket",
        "reference_name": name,
        "content": comment,
    }
    return await _call(_client().create_doc("Comment", doc))


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
