# Developer limits

## Implemented boundaries

- **25,000 requests:** shared across the entire installation, organizations, projects, keys and replicas connected to the same PostgreSQL database. UTC calendar month. Each committed bounded admission counts once; streams count once, not per chunk. Rejected validation/budget requests do not count. Provider failures, unknown outcomes and cancellations after admission still count. A retried request is a new admission. Counts survive restarts and are included in database backups.
- **Two users:** at most two dashboard login accounts, including the bootstrapped administrator. At most two governed member records are also allowed. These are separate identity directories; the limit does not prove that accounts belong to two distinct natural persons. Existing records can be updated at capacity; deletion frees a slot. Blocked member records still occupy a slot.
- **Three projects:** installation-wide, not three per department. Existing projects remain editable. Creation is serialized across replicas. Existing data above a limit is preserved; additional creation is refused.
- **Seven days of searchable history:** request ledger detail, denial detail, administrative audit and key-reassignment detail use a database-clock cutoff. Explicit older date filters cannot bypass it. Financial aggregates, unsettled reservations, billing evidence and backups retain older records so budgeting and reconciliation stay correct. This is a search-window limit, not automatic deletion or a seven-day retention promise.

## Packaged enforcement

The official compiled proxy always selects durable PostgreSQL bounded admission and verifies the bundled signed entitlement against its compiled issuer key. Environment variables cannot disable these checks. Installation owners still control the operating system and database; this is not tamper-proof or a cross-installation account quota.
