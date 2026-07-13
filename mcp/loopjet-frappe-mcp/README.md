# Loopjet Frappe MCP

Remote MCP server for Loopjet ERPNext invoices and Frappe Helpdesk tickets.

## Authentication

Each user authenticates with their own Frappe API key and secret:

```text
Authorization: Bearer <frappe_api_key>:<frappe_api_secret>
```

The MCP server validates the token with Frappe and forwards every request to
Frappe as that user. Frappe roles and permissions remain the source of truth.

## Runtime

```bash
FRAPPE_BASE_URL=https://erp.loopjet.io \
MCP_RESOURCE_SERVER_URL=https://mcp.loopjet.io \
python -m loopjet_frappe_mcp.server
```

The MCP endpoint is:

```text
/mcp
```

## Guardrails

- Invoices are created as drafts.
- No delete/cancel/submit tools are exposed.
- Service periods are optional, but if one date is provided then both start and
  end dates are required.
- Reverse charge is an explicit boolean field.
