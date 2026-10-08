# TollGate Developer

Self-hosted budget controls for supported OpenAI and Anthropic API requests.
**Free Developer preview: 25,000 requests/month, 2 users and 3 projects.**

This repository distributes installers, documentation and compiled releases.
The current core source is private. The packaged Developer edition is free to use
under [its distribution terms](LICENSE); it is not an unrestricted open-source edition.
Your AI traffic and provider keys stay on your infrastructure. Provider and
infrastructure charges are separate.

## Existing installations: v0.2.2 update

**v0.2.2 is an update for existing v0.2.1 preview installations, not a fresh-install launch.**
See [the update instructions](docs/UPDATE-0.2.2.md) for the tested proxy/dashboard update.
A Git pull alone does not replace your running Docker images.

## Fresh installations — on hold

> **New deployments should await gateway licensing clearance.** The existing
> identity gateway’s enterprise-code licensing clearance remains unresolved.
> v0.2.2 updates only the proxy and dashboard; it does not resolve that issue.
> The baseline steps below are retained for reference, not as an invitation
> to start a new deployment. Existing preview users should use the update
> instructions above.

Requires Docker Engine with Compose v2, Python 3.10+, 8 GB available RAM and
15 GB free disk. This release targets Linux x86-64. Apple Silicon requires
x86 emulation and is supported only as a local development preview.

1. Read the [v0.2.1 package licence](https://github.com/Sanrish-Tech/tollgate-developer/blob/v0.2.1/LICENSE) beside the download: it governs permitted use, allowances, expiry, support and liability.
   Download `tollgate-developer-0.2.1.tar.gz`, `runtime-images.tar.gz` and
   `SHA256SUMS` from [the release](https://github.com/Sanrish-Tech/tollgate-developer/releases/tag/v0.2.1).
2. In the download directory, verify both archives:

   ```sh
   shasum -a 256 -c SHA256SUMS
   tar -xzf tollgate-developer-0.2.1.tar.gz
   cd tollgate-developer-0.2.1
   cat LICENSE
   ```

   Review the displayed package licence before continuing. It allows internal
   commercial workloads within the preview allowances; provider costs are separate.
   This display does not change the licence or add a click-through agreement.

   ```sh
   docker load -i ../runtime-images.tar.gz
   python3 setup.py
   ```

3. Edit `.local/provider.env` locally to add your own OpenAI and/or Anthropic
   API key. Never share or commit this file. Unconfigured providers refuse calls.
4. Start and create the first organization with a $5 budget:

   ```sh
   docker compose --env-file .local/installation.env up -d --wait
   python3 distribution/finish-setup.py .local --budget 5
   ```

Open **http://localhost:3000**. Sign in as `admin` using `ADMIN_PASSWORD` from
`.local/installation.env`. Create a department, project, member and personal key.
Set a project budget and allowed model before sending requests. Use the personal
key in your application, never the administrator key. The API base URL is
**http://localhost:4000/v1**.

Setup and health checks make no paid model calls. Model requests that you choose
to send are billed by your provider. Database, Redis and identity gateway ports
are not published; dashboard and API bind to localhost. Review
[operations](docs/OPERATIONS.md) before remote access or production workloads.

## Included allowances

| Item | Developer allowance |
| --- | --- |
| Requests | 25,000 admitted requests per installation per UTC calendar month |
| Users | 2 dashboard accounts, including admin; 2 governed member records |
| Projects | 3 across the installation |
| Searchable detailed history | 7 days |
| Storage | Self-managed; financial state and backups are retained separately |
| Support | Documentation and best-effort issue responses; no promised hours or SLA |

Admitted requests count even if a provider times out. Requests rejected before
admission do not count. Counters are stored in PostgreSQL and survive application
restarts; concurrent requests share the same limit. The next month restores the
request allowance. More than 25,000 requests are refused before provider forwarding.
The 7-day search window is **not automatic database deletion**. See
[limits](docs/DEVELOPER-LIMITS.md) for exact counting and retention behavior.

The official binaries verify a signed entitlement and do not offer an environment
switch to disable licensing or the quotas. Customer-controlled software cannot
be made tamper-proof. These are installation allowances, not a globally metered
account across independently created installations.

## Supported scope and current deadlines

This preview supports reviewed OpenAI Responses/Chat and Anthropic Messages
paths, including supported streaming. See [model contracts](docs/MODEL-CONTRACTS.md).
Only requests routed through TollGate are governed. This is not a guarantee for
all Cursor/agent traffic or arbitrary $0.15 responses. Provider-hosted tools,
embeddings, audio/video/realtime and image generation are excluded.

**Provider profiles expire October 14, 2026 inclusive UTC.** After expiry, new
requests using those profiles are refused until a reviewed update is installed.
The separate signed Developer entitlement expires **October 6, 2027 at 00:00 UTC**.
Changing local dates in a profile does not renew a reviewed contract. These
requirements make this a developer preview, not an unattended production release.

Reservations use conservative ceilings; a small budget may reject a request that
would ultimately have cost less. Uncertain provider outcomes retain their funds
until reconciliation. Do not delete financial records to release funds.

## More capacity or help

[Book a technical pilot](https://calendly.com/rishit-trytollgate/30min) or email
[info@trytollgate.com](mailto:info@trytollgate.com) for Team, Business or Enterprise.
Paid deployment, support coverage and response commitments are agreed before
purchase. SSO/SCIM and automated subscription billing are not included in this preview.

Use GitHub issues for reproducible bugs without secrets. Security reports belong
at info@trytollgate.com. Keep provider keys, passwords, prompts and private ledgers
out of public issues.
