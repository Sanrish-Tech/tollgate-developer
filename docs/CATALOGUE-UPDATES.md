# Signed model catalogue updates

This is updater groundwork for existing installations. It is not a fresh-install release and does not change the gateway licensing hold described in the README.

TollGate catalogue bundles contain `manifest.json`, `manifest.signature.json` and `profiles.json`. Verify them with the separately trusted catalogue public-key ring; a key included only inside the downloaded bundle is not a trust anchor. The verifier requires Python and `cryptography==50.0.1`.

```sh
python3 distribution/catalogue/update.py /absolute/catalogue-bundle \
  --destination "$PWD/distribution/direct-profiles.json" \
  --keys /absolute/trusted-catalogue-public-keys.json \
  --channel developer
```

The command verifies the Ed25519 signature, exact manifest bytes, profile hash, profile count, channel and monotonic catalogue version before an atomic replacement. A failure leaves the installed file unchanged. Verified bundles are retained under `distribution/.catalogue-history/`; local state is owner-only in `distribution/.catalogue-state.json`.

Rollback is explicit and must point to a previously verified bundle:

```sh
python3 distribution/catalogue/update.py "$PWD/distribution/.catalogue-history/vVERSION" \
  --destination "$PWD/distribution/direct-profiles.json" \
  --keys /absolute/trusted-catalogue-public-keys.json \
  --channel developer --rollback
```

Stop inference and take a verified backup before changing profiles. A profile update never rewrites historical financial records. The compiled runtime still enforces its own reviewed contract and release digest, so a signed JSON bundle cannot make an unqualified model dispatchable. Restart with a release that explicitly names the catalogue version, then run the offline smoke check before reopening ingress.

Catalogue polling is bounded rather than instantaneous. Published status must include the last successful source fetch, current fetch failures and the stated maximum detection delay. A missing provider listing is not a deletion or retirement signal; retirement requires an explicit official date and is enforced on that date.
