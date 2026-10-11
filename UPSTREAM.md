# Upstream versions

This store reuses only official Umbrel specifications and upstream Open-Source releases. No forks, no custom builds.

## Templates and references

| Source | Ref | Date / note |
|---|---|---|
| `getumbrel/umbrel-community-app-store` (template) | commit `1b147ae7209f42ef37917a94af2d99cf5b77cc7d` (`master`) | 2024-04-08, "Revise instructions in README.md" — newest stable state at store creation (2026-10-11) |
| `getumbrel/umbrel-apps` (official store, manifest conventions) | commit `aa3c4e9` (`master`) | 2026-10-08 — manifests of n8n, anything-llm, grafana, ollama, uptime-kuma reused 1:1 (adapted only for store id/prefix) |
| umbrelOS target | 2.x | Port ranges, `app_proxy` pattern, `exports.sh`/`derive_entropy` convention per official packaging |

Upstream changes are reviewed regularly; dependency bumps arrive as Renovate PRs (see `renovate.json`).

## Pinned application versions (store creation, 2026-10-11)

| App | Upstream version | Image (tag + digest) |
|---|---|---|
| tasiomind-neo4j | 5.26.31 LTS (Community) | `neo4j:5.26.31-community@sha256:c7d25c…2237c67ce8069` |

Previously shipped apps already available in the official Umbrel App Store
(n8n 2.42.4, AnythingLLM 1.17.0, Ollama 0.40.0, Grafana 13.2.3, Uptime Kuma 2.5.5)
were removed from this store on 2026-10-11 to avoid duplication; their manifests
had been reused 1:1 from `getumbrel/umbrel-apps@aa3c4e9`.

Full digests are in each app's `docker-compose.yml`. No `latest` tags anywhere.
