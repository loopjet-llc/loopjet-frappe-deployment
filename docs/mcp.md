# Loopjet Frappe MCP

The deployment includes a separate MCP sidecar for AI agents that need controlled
access to the Loopjet Frappe stack without using the Frappe web UI.

## URL

Production endpoint:

```text
https://mcp.loopjet.io/mcp
```

## Authentication

Every team member should use their own Frappe API key and API secret.

MCP client header:

```text
Authorization: Bearer <frappe_api_key>:<frappe_api_secret>
```

The MCP server validates the token against Frappe and forwards all API calls to
Frappe as that same user. Frappe roles and permissions stay authoritative.

Do not use an Administrator key for daily agent work.

## Tools

Generic Frappe control tools:

- `whoami`
- `list_doctypes`
- `get_doctype_meta`
- `list_documents`
- `get_document`
- `create_document`
- `update_document`
- `delete_document`
- `submit_document`
- `cancel_document`
- `apply_workflow_action`
- `get_document_count`
- `search_link`
- `list_reports`
- `run_report`
- `list_print_formats`
- `get_pdf_url`
- `add_comment_to_document`
- `assign_document`
- `call_frappe_method`

Loopjet convenience tools:

- `list_customers`
- `get_customer`
- `list_invoices`
- `get_invoice`
- `create_draft_invoice`
- `update_draft_invoice`
- `get_invoice_pdf_url`
- `list_tickets`
- `get_ticket`
- `create_ticket`
- `update_ticket_status`
- `add_ticket_comment`

`delete_document`, `submit_document`, and `cancel_document` require
`confirm=true` so agents do not accidentally perform destructive or accounting
state-changing actions.

`call_frappe_method` can call whitelisted Frappe methods. Use it when no
purpose-built tool exists, and prefer regular document/report tools where
possible.

## Invoice rules

- New invoices are created as drafts.
- `service_period_start` and `service_period_end` are optional.
- If either service-period date is supplied, both must be supplied.
- `reverse_charge_applies` is explicit. When true, the connector sets the
  reverse-charge checkbox and sends an empty taxes table.

## Examples

List invoices:

```json
{
  "doctype": "Sales Invoice",
  "fields": ["name", "customer", "status", "grand_total", "modified"],
  "filters": [["Sales Invoice", "docstatus", "=", 0]],
  "limit": 20
}
```

Create a CRM Lead:

```json
{
  "doctype": "CRM Lead",
  "document": {
    "lead_name": "Example GmbH",
    "email": "hello@example.com"
  }
}
```

Run a report:

```json
{
  "report_name": "Accounts Receivable",
  "filters": {
    "company": "Loopjet LLC"
  }
}
```

## DNS

Point `mcp.loopjet.io` to the VPS before exposing the hosted endpoint.
