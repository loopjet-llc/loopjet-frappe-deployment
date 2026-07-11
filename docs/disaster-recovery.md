# Backup and disaster recovery

`scripts/backup.sh` captures each site's database plus public and private files.
Production backups must additionally be encrypted and copied to storage outside
the VPS. A backup that has never been restored is not considered verified.

Recommended policy:

- Local encrypted snapshot every 6 hours
- Daily off-site copy
- 14 daily, 8 weekly, and 12 monthly restore points
- Quarterly full restore drill into an isolated environment
- Alert on missed backup, low disk, or failed verification

Record image digests and `config/versions.json` with each backup so application
code and database state can be restored as a matched set.
