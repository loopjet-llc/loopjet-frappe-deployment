# Loopjet Frappe MCP

The deployment includes a separate MCP sidecar for AI agents that need controlled
access to ERPNext invoices and Frappe Helpdesk tickets.

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

Current tools:

- `whoami`
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

The server intentionally does not expose delete, cancel, or submit tools.

## Invoice rules

- New invoices are created as drafts.
- `service_period_start` and `service_period_end` are optional.
- If either service-period date is supplied, both must be supplied.
- `reverse_charge_applies` is explicit. When true, the connector sets the
  reverse-charge checkbox and sends an empty taxes table.

## DNS

Point `mcp.loopjet.io` to the VPS before exposing the hosted endpoint.
