# Operations

This release is a local developer preview. Default published ports bind to 127.0.0.1. In production use trusted TLS, secure cookies, restricted ingress, scoped provider keys and a tested backup/restore process. Do not expose Postgres, Redis, the identity gateway or the Docker socket.

To use different local ports, edit `PROXY_PORT` and `DASHBOARD_PORT` in `.local/installation.env` before starting. `finish-setup.py` uses the configured proxy port. Do not run setup again over an existing `.local` folder: it intentionally refuses to replace credentials.

## Backup

From the repository root:

```sh
python3 distribution/backup.py . /absolute/private/path/new-backup --verify-restore
```

This stops currently running applications, dumps the database, copies dashboard state and private configuration, records checksums, and resumes only the applications it stopped. The output contains secrets. Keep it off GitHub and out of public storage. Verify every checksum and restore the database into an isolated disposable environment before relying on a backup. Never overwrite a live financial database to test a restore.

## Profiles and upgrades

Current review deadline: October 14, 2026 inclusive UTC. Missing/expired profiles refuse requests. Check release updates before expiry. Do not extend the JSON dates yourself or remove the digest gate. The profile digest is checked inside the compiled release.

Before an upgrade: stop inference, preserve financial/audit evidence, take and verify a backup, inspect release notes and profile changes, then load the new release images and test health. Keep the previous runtime archive and backup for recovery; a software rollback alone does not reverse schema changes.

## Incidents

Close inference ingress first. Preserve unresolved reservations and provider evidence. Never clear Redis, reset budgets or delete ledger entries to release uncertain holds. Confirm the provider outcome before reconciliation. Calls made around TollGate remain outside its budgets.

Developer quotas are enforced locally. Automated subscription/overage billing is not included. Documentation and best-effort issue responses are supplied; no guaranteed support hours, response time, 24×7 support or uptime SLA are included.

## Signed entitlement

Backups include the public Developer licence as well as private credentials. Licence checks run offline; no licence server receives prompts or usage. Renew before October 6, 2027 at 00:00 UTC. Missing, modified or expired entitlements refuse model requests. The earlier provider-profile deadline is independent.
