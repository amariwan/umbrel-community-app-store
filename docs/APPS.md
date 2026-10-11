# App research and selection

Selection rule: **no app is included for fame alone** — every app must be installable
on umbrelOS 2.x (single-container or simple compose, `app_proxy`-compatible,
no privileged/host-network requirements, persistent data dir).

## Included

| App | Category | Upstream | Why |
|---|---|---|---|
| tasiomind-n8n (2.42.4) | automation | n8n-io/n8n, fair-code | Workflow automation backbone; manifest reused from official Umbrel packaging |
| tasiomind-anythingllm (1.17.0) | ai | Mintplex-Labs/anything-llm | Local knowledge base + agents; works with Ollama for fully local RAG |
| tasiomind-ollama (0.40.0) | ai | ollama/ollama | Local LLM runtime; GPU permission declared per convention |
| tasiomind-grafana (13.2.3) | networking | grafana/grafana | Monitoring dashboards; includes upstream CVE fixes (see release notes) |
| tasiomind-uptime-kuma (2.5.5) | networking | louislam/uptime-kuma | Lightweight uptime monitoring with 70+ notifiers |
| tasiomind-neo4j (5.26.31 LTS) | developer | neo4j/neo4j (Community) | Graph DB for knowledge graphs / AI second-brain (e.g. Graphiti backends) |

## Evaluated but deliberately excluded

| Candidate | Reason |
|---|---|
| Kestra | Java-based orchestrator needing Postgres + Elasticsearch (or heavy standalone). Too resource-hungry for Pi-class umbrelOS devices and too much custom compose to maintain. Revisit if an official lightweight packaging appears. n8n covers automation in this store. |
| Graphiti (Zep) | A Python library / MCP server, not a standalone one-click app with an official server container and UI. Cannot be packaged honestly as an Umbrel app today. Use `tasiomind-neo4j` as its graph backend and run Graphiti alongside your agent code. |
| Portainer, Node-RED, Watch-Your-LAN | Valid, but add maintenance surface without covering a new priority. The store stays small on purpose; proposals welcome via issues. |

## Resource guidance (approx., x86/ARM)

- Ollama needs RAM per model (check model requirements; oversized models can hang small devices).
- Neo4j heap is capped at 1G in compose; raise only on capable hardware.
- AnythingLLM + Ollama together are the heaviest combo; n8n/Grafana/Uptime Kuma are light.
