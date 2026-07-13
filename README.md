# Loopjet Frappe Platform

Reproducible development and production deployment for ERPNext, Frappe HR,
Frappe CRM, and Frappe Helpdesk, extended by `loopjet_frappe_custom`.

The platform is built from reviewed, pinned upstream releases. Product code is
never edited in this repository. Loopjet behavior belongs in the custom app.

## Topology

| Site | Applications |
| --- | --- |
| `erp.localhost` | ERPNext, Frappe HR, Loopjet Custom |
| `crm.localhost` | Frappe CRM, Loopjet Custom |
| `helpdesk.localhost` | Frappe Helpdesk, Loopjet Custom |

All sites use one immutable application image but have independent databases.
Production hostnames are supplied through environment variables.

## Quick start

```bash
cp .env.example .env
./scripts/build-image.sh
./scripts/stack.sh local up -d
./scripts/create-sites.sh
./scripts/healthcheck.sh
```

Open `http://erp.localhost:8080`, `http://crm.localhost:8080`, and
`http://helpdesk.localhost:8080`.

## Operations

- [Architecture](docs/architecture.md)
- [Development](docs/development.md)
- [MCP server](docs/mcp.md)
- [Production and Hostinger VPS](docs/production.md)
- [Upgrades](docs/upgrades.md)
- [Backup and disaster recovery](docs/disaster-recovery.md)
- [Security](SECURITY.md)

Never run an unreviewed `bench update` in production. Upgrade by changing the
version lock, validating a new image, restoring a production backup in staging,
and promoting the exact tested image digest.
