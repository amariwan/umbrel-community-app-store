# Testing

## Automated validation (2026-10-11, run locally + in CI)

- `python3 scripts/validate.py` — store id/name, required manifest fields, id prefix,
  category allowlist, unique non-reserved ports, gallery present, numeric pinned versions,
  digest-pinned images (no `latest`), manifest-version/image-tag match, no `privileged` /
  host networking / `ports:`, `cap_add` allowlist, volumes inside `${APP_DATA_DIR}`,
  no hardcoded secrets, `exports.sh` completeness with `derive_entropy` for secrets,
  `app_proxy` wiring. **Result: all checks passed (6 apps).**
- Negative test: a scratch app with `latest` tag, `ports:` publishing, wrong `APP_HOST`
  and duplicate port was correctly rejected (5 problems found), then removed.
- `docker compose config` per app (with umbrelOS-injected `app_proxy` stripped and
  documented placeholder env): **all 6 configs valid.**
- `renovate.json` is valid JSON and references all 6 manifest/container pairs.
- GitHub Actions workflow `.github/workflows/validate.yml` repeats all of the above on
  every push/PR.

## Real-hardware test

**Not performed — no compatible umbrelOS 2.x hardware was available for this delivery.**
No successful install on real hardware is claimed.

Before first production use, the operator must verify on a compatible umbrelOS installation:

1. Settings → Community App Stores → add `https://github.com/amariwan/umbrel-community-app-store`.
2. Confirm the store appears as "tasiomind App Store" with all 6 apps.
3. Install at least one app (suggested: `tasiomind-uptime-kuma`, lowest resource needs),
   open it via the dashboard, then uninstall and confirm `${APP_DATA_DIR}` handling.
4. Record the result here (device, umbrelOS version incl. beta if used, app, outcome).
