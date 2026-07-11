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

## Required external inputs

Final deployment requires the VPS address and SSH access, production hostnames,
the TLS notification address, outbound email configuration, and an encrypted
off-site backup destination. These values are never committed to GitHub.
