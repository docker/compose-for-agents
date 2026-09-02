# Cloudflare Deployment (Wrangler)

This folder deploys a Cloudflare Worker UI that interacts with your MCP Gateway. It includes bindings for KV, R2, D1, and Durable Objects. You can later connect a Cloudflare Container service for the gateway, or reference a public gateway URL.

Setup
1) Install Wrangler: npm i -g wrangler
2) Copy wrangler.toml and set:
   - account_id (or pass via env)
   - vars.GATEWAY_URL (public URL of your MCP Gateway)
   - Fill resource bindings (KV namespace id, R2 bucket name, D1 database info)
3) Create resources:
   - KV: wrangler kv namespace create UI_STATE
   - R2: wrangler r2 bucket create <bucket-name>
   - D1: wrangler d1 create MCP_DB
   - DO: first deploy will create migration v1 for SessionDurable
4) Preview: wrangler dev
5) Deploy: wrangler deploy

Optional: Cloudflare Containers (Beta)
- If you run your MCP Gateway on Cloudflare Containers as service "mcp-gateway", add a service binding in wrangler.toml and adjust worker to call that service instead of external GATEWAY_URL.

Security
- Do not expose your MCP Gateway publicly without authentication. Consider placing it behind Cloudflare Access and calling from the Worker using service bindings or mTLS.
