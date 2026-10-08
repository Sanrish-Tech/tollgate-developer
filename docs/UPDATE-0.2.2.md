# Update an existing v0.2.1 installation to v0.2.2

This update replaces the proxy and dashboard only. Keep your existing database,
Redis and identity gateway images. It does not redistribute or clear the separate
identity gateway enterprise-code licensing question. New deployments should await
that clearance; this update is for existing preview installations.

Download `developer-core.tar.gz`, `compose.runtime-update.yml` and `SHA256SUMS`
from the v0.2.2 release. Read the existing package LICENSE; the same terms,
allowances, provider-profile validity and entitlement expiry continue to apply.

1. Pause application traffic and make a verified backup using the existing
   backup instructions in OPERATIONS.md. Keep `.local`, volumes and financial state.
2. Put the three downloaded files in your existing installation directory.
3. Verify and load the update:

```sh
shasum -a 256 -c SHA256SUMS
docker load -i developer-core.tar.gz
docker compose --env-file .local/installation.env stop proxy dashboard
docker compose --env-file .local/installation.env -f compose.yml -f compose.runtime-update.yml up -d --wait
```

Use BOTH compose files in future start/stop/update commands. Never use `down -v`.
Upgrade every proxy replica together; mixed old and new enforcement is unsupported.
Existing Observe selection migrates to Soft cap. Historical accounting remains intact.
Verify login, Provider setup, theme control, project/member/key creation and your
budget settings before resuming traffic. Model requests incur your provider charges.

## Changes

- Theme control beside the account controls; Provider setup and Pending charges navigation.
- Project budget form validation and parent-budget guidance.
- Explicit project membership confirmation when assigning an existing key owner.
- Observe replaced by Soft cap: a crossing request may exceed the cap, but subsequent
  requests are refused while settled spend plus reservations is at or above the cap.
- Blocked request counts no longer presented as monetary savings.
- Unsupported advanced policies rejected at creation/activation; existing incompatible
  policies return a clear conflict and can be disabled or removed.
- Reused provider connections, clearer uncertain-charge diagnostics and audited manual review.
- Proven connection/pool failures before dispatch settle at zero; uncertain dispatched
  outcomes retain their holds. No automatic replay that could duplicate a charge.
- Demo seeding commands and the seeder itself removed from these runtime images.

Existing seeded records are not deleted. The original project-deletion finding and
full organization-membership usability acceptance remain open. Automatic reconciliation
of ambiguous provider outcomes is not claimed. Provider profiles still expire
October 14, 2026 inclusive UTC; this update does not silently extend them.

## Verification

Private source CI passed. The compiled candidate booted with PostgreSQL and the
identity gateway and passed licence rejection, concurrent monthly-quota, persistent
quota, project-limit and member-limit tests with a mocked provider and zero paid calls.
Source revision: bed6b72 (October 8, 2026). Customer retesting remains required.
