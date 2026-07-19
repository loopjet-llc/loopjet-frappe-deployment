# Production on a Hostinger VPS

## Minimum baseline

Use a current 64-bit Ubuntu LTS VPS with at least 4 vCPU, 8 GB RAM, and SSD
storage. Sixteen GB RAM is preferred when staging and production share a host.

## Host preparation

1. Create a non-root deploy user with SSH keys and limited sudo access.
2. Disable password SSH login and root SSH login.
3. Allow only SSH, HTTP, and HTTPS through the firewall.
4. Install Docker Engine and its Compose plugin from Docker's official packages.
5. Point ERP, CRM, and Helpdesk DNS records to the VPS.
6. Authenticate Docker to GitHub Container Registry using a least-privilege token.
7. Clone this repository, create `.env`, and use generated unique secrets.
8. Run `./scripts/stack.sh production up -d` and `STACK_MODE=production ./scripts/create-sites.sh`.

The production composition adds Traefik with automatic Let's Encrypt certificates.
Do not expose MariaDB or Redis ports publicly.

Loopjet uses one connected Frappe site. `ERP_SITE` is the canonical site and
installs ERPNext, HRMS, Frappe CRM, Frappe Helpdesk, Telephony, and the Loopjet
custom app into one database. Raven is installed on the same site at `/raven`
so system users can message one another and link ERP records in conversations.
`CRM_SITE` and `HELPDESK_SITE` are domain aliases for that same site, which keeps
leads, deals, quotations, invoices, customers, contacts, tickets, and chat
available through one user directory.

## Existing Hostinger Docker and Traefik VPS

When Hostinger's Traefik project already owns ports 80 and 443, keep it in place
and set `STACK_MODE=hostinger`. The Hostinger mode adds routing labels to the
Frappe frontend but does not start another proxy or publish MariaDB, Redis, or
Frappe ports on the host.

Set the production hostnames in `ERP_SITE`, `CRM_SITE`, and `HELPDESK_SITE`, add
all three hosts to `SITES_RULE`, set `ERP_COMPANY` to the ERPNext company name,
and set `HEALTHCHECK_SCHEME=https` and `HEALTHCHECK_PORT=443`. Start and
initialize the stack with:

```sh
./scripts/stack.sh hostinger up -d
STACK_MODE=hostinger ./scripts/create-sites.sh
./scripts/healthcheck.sh
```

The MCP sidecar is routed separately through `MCP_SITE`, usually
`mcp.loopjet.io`. Add that DNS record to the same VPS and expose
`https://mcp.loopjet.io/mcp` to MCP clients. Team members authenticate with
their own Frappe API key and secret using:

```text
Authorization: Bearer <frappe_api_key>:<frappe_api_secret>
```

## Required external inputs

Final deployment requires the VPS address and SSH access, production hostnames,
the TLS notification address, outbound email configuration, and an encrypted
off-site backup destination. These values are never committed to GitHub.
