# Upgrade procedure

Upstream mirror synchronization is intentionally separate from deployment.
A scheduled workflow proposes version-lock updates as pull requests.

Every upgrade must pass this sequence:

1. Review upstream release notes and breaking changes.
2. Build a new image from the proposed lock.
3. Prove fresh installation of all three site profiles.
4. Restore a recent production backup into staging.
5. Run all migrations, background workers, and application smoke tests.
6. Obtain manual production approval.
7. Capture a fresh database and file backup.
8. Deploy the exact tested image digest and migrate sites.
9. Validate business-critical workflows before leaving maintenance mode.

Rolling back application code alone is unsafe after database migrations. Restore
the matching pre-upgrade database and files together with the previous image.
