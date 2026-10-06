# Release validation

Developer 0.2.1 is a compiled Linux x86-64 developer preview.

Local packaged checks on October 6, 2026 verified startup of all five services,
authenticated dashboard login, rejection of unauthenticated dashboard access,
and offline signed entitlement validation. Disabling licensing by environment
variable did not bypass verification. The compiled proxy was tested with real
PostgreSQL and the real identity gateway, with model responses supplied by an
in-memory fixture: eight concurrent requests competing for the last monthly
slot resulted in exactly one provider-fixture call and seven quota denials.
A fresh accounting authority still refused the next request. Project creation
stopped at three and member creation at two; the compiled dashboard refused a
third login account.

All layers of both core images were inspected for application Python/C source,
bytecode and credential paths. Only compiled application modules and empty
package initializers were present; third-party Python dependencies remain under
their own licences. This does not establish resistance to reverse engineering.

The private source revision previously passed 197 isolated PostgreSQL/provider-
fixture checks and 212 unit checks (72 environment-dependent checks skipped).
Those source tests are distinct from the packaged acceptance checks above.
No paid provider calls were made during Developer packaging acceptance.

The GitHub release workflow independently installs the downloadable archives on
Linux x86-64 and verifies backup/restore. Check its current result before relying
on that additional validation. It makes no model calls. This preview has not
been qualified for production throughput, high availability, every Cursor
workflow, or every provider feature.

0.2.1 also fixes dashboard startup readiness and updates urllib3/PyJWT in the proxy and identity gateway for upstream security fixes. The 0.2.0 public preview was withdrawn.

The final five runtime images were scanned with a refreshed October 6 vulnerability database: no high or critical findings were reported. This is a point-in-time scan, not a guarantee of absence of vulnerabilities.
