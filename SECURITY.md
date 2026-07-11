# Security policy

- Keep `.env`, database dumps, site files, SSH keys, and registry credentials out of Git.
- Use unique generated database and Administrator passwords in every environment.
- Expose only ports 22, 80, and 443 on the VPS.
- Encrypt backups and copy them off the VPS.
- Pin deploys to immutable image digests after staging validation.
- Review GPLv3 and AGPLv3 source obligations before distributing modifications.

Report security concerns privately to `engineering@loopjet.com`.
