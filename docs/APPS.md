# App research and selection

Selection rules:

1. **No duplicates of the official Umbrel App Store.** n8n, AnythingLLM, Ollama,
   Grafana and Uptime Kuma are already available officially — they were removed
   from this store on 2026-10-11 and will not be re-added.
2. **No app is included for fame alone** — every app must be installable
   on umbrelOS 2.x (single-container or simple compose, `app_proxy`-compatible,
   no privileged/host-network requirements, persistent data dir).

## Included

| App | Category | Upstream | Why |
|---|---|---|---|
| tasiomind-neo4j (5.26.31 LTS) | developer | neo4j/neo4j (Community) | Graph DB for knowledge graphs / AI second-brain (e.g. Graphiti backends) |

## Evaluated but deliberately excluded

| Candidate | Reason |
|---|---|
| n8n, AnythingLLM, Ollama, Grafana, Uptime Kuma | Already in the official Umbrel App Store — no duplication in this store. |
| Kestra | Java-based orchestrator needing Postgres + Elasticsearch (or heavy standalone). Too resource-hungry for Pi-class umbrelOS devices and too much custom compose to maintain. Revisit if an official lightweight packaging appears. |
| Graphiti (Zep) | A Python library / MCP server, not a standalone one-click app with an official server container and UI. Cannot be packaged honestly as an Umbrel app today. Use `tasiomind-neo4j` as its graph backend and run Graphiti alongside your agent code. |
| Portainer, Node-RED, Watch-Your-LAN | Valid, but already official or adding maintenance surface without covering a new priority. The store stays small on purpose; proposals welcome via issues. |

## Resource guidance (approx., x86/ARM)

- Neo4j heap is capped at 1G in compose; raise only on capable hardware.
