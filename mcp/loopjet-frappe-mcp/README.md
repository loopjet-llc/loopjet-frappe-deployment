# Loopjet Frappe MCP

Remote MCP server for Loopjet's Frappe stack: ERPNext, CRM, HR, and Helpdesk.
It exposes broad Frappe document control without requiring the web UI.

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

## Tool coverage

Generic Frappe tools:

- inspect DocTypes and metadata
- list, get, create, update, and delete documents
- submit, cancel, and apply workflow actions
- count documents
- run reports
- search link fields
- list print formats and generate PDF URLs
- add comments
- assign documents with ToDos
- call whitelisted Frappe methods

Loopjet-specific convenience tools:

- customers
- draft invoices
- invoice PDF URLs
- Helpdesk tickets

## Guardrails

- Invoices are created as drafts.
- Delete, submit, and cancel require `confirm=true`.
- Service periods are optional, but if one date is provided then both start and
  end dates are required.
- Reverse charge is an explicit boolean field.
- Every request is still executed by Frappe as the API-key owner, so Frappe
  roles and permissions remain authoritative.
