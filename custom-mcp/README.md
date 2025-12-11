# Custom MCP Gateway Stack

This example wires a Docker MCP Gateway with a flexible set of MCP servers and secrets loaded from a `.mcp.env` file.

Prerequisites
- Docker Desktop 4.43+ or Docker Engine with Compose v2.38.1+
- Optional: Docker Model Runner if you plan to use local models

Setup
1. cd custom-mcp
2. cp mcp.env.example .mcp.env
3. Fill in required secrets (e.g., GITHUB_TOKEN for `github-official`).

Run
- Start the stack:
  docker compose up --build

- The gateway will listen on port 8811. A health endpoint is available at:
  http://localhost:8811/health

Modify servers
- Edit compose.yaml and add or remove `--servers=...` entries on the mcp-gateway service.
- If a server needs credentials, add them to `.mcp.env` and reference via `--secrets=...` if required.

Notes
- The example includes a minimal curl-based `mcp-client` container that checks gateway health.
- To integrate with an agent, set its MCP server URL to the gateway endpoint, e.g. `http://mcp-gateway:8811/sse` for SSE transport.
