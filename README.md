# tasiomind App Store for umbrelOS

Community App Store for [umbrelOS](https://umbrel.com) 2.x — a small, curated,
low-maintenance store. It intentionally contains **no duplicates of the official
App Store**: n8n, AnythingLLM, Ollama, Grafana and Uptime Kuma are already
available officially and are therefore not shipped here.

- Store ID: `tasiomind` · Store name: `tasiomind` · App prefix: `tasiomind-`
- Repository: https://github.com/amariwan/umbrel-community-app-store
- Upstream template state and pinned versions: see [UPSTREAM.md](UPSTREAM.md)
- App research (incl. rejected candidates): see [docs/APPS.md](docs/APPS.md)
- Validation results + hardware-test status: see [docs/TESTING.md](docs/TESTING.md)

## Apps

| App | What | UI port |
|---|---|---|
| tasiomind-neo4j | Graph database (5.26 LTS Community, incl. APOC) | 7474 |

## Installation

1. Open your umbrelOS dashboard → **App Store → … → Community App Stores**
   (or **Settings**, depending on your umbrelOS version).
2. Add this URL: `https://github.com/amariwan/umbrel-community-app-store`
3. The **tasiomind App Store** appears alongside the official store.
4. Install the app with one click.

## Updates

- [Renovate](renovate.json) opens PRs for container and manifest updates every weekend.
  Patch/minor/security PRs merge manually after CI; **major upgrades never merge
  without a compatibility check** (umbrelOS 2.x conventions + data persistence).
- Every push/PR runs manifest, policy, and compose validation
  (`.github/workflows/validate.yml`, `scripts/validate.py`).
- All images are digest-pinned — no floating `latest` tags.

## Security and conventions

- Official Umbrel app conventions: `app_proxy` routing, `${APP_DATA_DIR}` persistence,
  `exports.sh` + `derive_entropy` for generated secrets — **no hardcoded secrets**.
- No privileged containers, no host networking, no host-port publishing, no extra capabilities.
- Data directories are never overwritten; upgrades keep `${APP_DATA_DIR}` volumes.

## Known limitations

- **Neo4j Bolt (7687) is not exposed to the LAN** — browser UI works via the dashboard,
  and in-app consumers reach Bolt at `tasiomind-neo4j_neo4j_1:7687`. External drivers need
  a self-managed port mapping.
- **Neo4j admin password is auto-generated** on install. Retrieve it on the device, e.g.
  via the app's runtime environment (`NEO4J_AUTH`), or back up `${APP_DATA_DIR}` regularly.
- Neo4j heap is capped at 1G in compose; raise only on capable hardware.
- Gallery images are upstream project logos as placeholders until on-device screenshots exist.
- **No on-device install test has been performed yet** (see [docs/TESTING.md](docs/TESTING.md)).
  umbrelOS 2.x compatibility follows from official-packaging reuse, not from a device run.

## Contributing

Proposals via GitHub issues. New apps must satisfy `scripts/validate.py` and the
selection rule in [docs/APPS.md](docs/APPS.md): genuinely installable on umbrelOS 2.x,
pinned digests, documented persistence. Major version bumps must note the compat check.
