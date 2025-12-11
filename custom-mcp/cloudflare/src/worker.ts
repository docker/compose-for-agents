export interface Env {
  GATEWAY_URL: string;
  UI_STATE: KVNamespace;
  ASSETS_BUCKET: R2Bucket;
  MCP_DB: D1Database;
  SESSION_DO: DurableObjectNamespace;
  // MCP_GATEWAY: Service; // if using service binding to container
}

export default {
  fetch: async (req: Request, env: Env, ctx: ExecutionContext): Promise<Response> => {
    const url = new URL(req.url);

    // Basic router
    if (url.pathname === "/") {
      return new Response(htmlPage(), { headers: { "content-type": "text/html; charset=utf-8" } });
    }

    if (url.pathname === "/api/health") {
      try {
        const resp = await fetch(`${env.GATEWAY_URL}/health`, {
          headers: { "accept": "text/plain" },
        });
        return new Response(await resp.text(), { status: resp.status, headers: { "content-type": "text/plain" } });
      } catch (e: any) {
        return Response.json({ error: e?.message ?? String(e) }, { status: 500 });
      }
    }

    if (url.pathname === "/api/config") {
      const servers = (await env.UI_STATE.get("servers")) ?? "duckduckgo,github-official,brave,wikipedia-mcp,postgres";
      return Response.json({ gateway: env.GATEWAY_URL, servers: servers.split(",") });
    }

    if (url.pathname === "/api/session") {
      // Example Durable Object-backed session counter
      const id = env.SESSION_DO.idFromName("global");
      const stub = env.SESSION_DO.get(id);
      return await stub.fetch(req);
    }

    return new Response("Not found", { status: 404 });
  }
};

export class SessionDurable {
  state: DurableObjectState;
  env: Env;
  constructor(state: DurableObjectState, env: Env) {
    this.state = state;
    this.env = env;
  }
  async fetch(_req: Request) {
    const key = "counter";
    let val = Number((await this.state.storage.get(key)) || 0) + 1;
    await this.state.storage.put(key, val);
    return Response.json({ counter: val });
  }
}

function htmlPage(): string {
  return `<!doctype html>
<html><head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Custom MCP Gateway UI (Cloudflare)</title>
<style>
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }
.card { border: 1px solid #ddd; border-radius: 8px; padding: 1rem; max-width: 800px; }
pre { background: #f7f7f7; padding: 0.75rem; border-radius: 6px; overflow: auto; }
button { padding: 0.5rem 1rem; margin-right: 0.5rem; }
</style>
</head>
<body>
  <h1>Custom MCP Gateway UI (Cloudflare)</h1>
  <div class="card">
    <p>This Worker lets you verify gateway health and view configured servers via KV.</p>
    <div>
      <button onclick="checkHealth()">Check Health</button>
      <button onclick="loadConfig()">Load Config</button>
      <button onclick="session()">Session Counter (DO)</button>
    </div>
    <h3>Health</h3>
    <pre id="health">(click Check Health)</pre>
    <h3>Config</h3>
    <pre id="config">(click Load Config)</pre>
    <h3>Session</h3>
    <pre id="session">(click Session Counter)</pre>
  </div>
  <script>
    async function checkHealth(){
      const el = document.getElementById('health');
      el.textContent = 'Loading...';
      try { const r = await fetch('/api/health'); el.textContent = await r.text(); } catch(e){ el.textContent = 'Error: '+e.message }
    }
    async function loadConfig(){
      const el = document.getElementById('config');
      el.textContent = 'Loading...';
      try { const r = await fetch('/api/config'); el.textContent = JSON.stringify(await r.json(), null, 2); } catch(e){ el.textContent = 'Error: '+e.message }
    }
    async function session(){
      const el = document.getElementById('session');
      el.textContent = 'Loading...';
      try { const r = await fetch('/api/session'); el.textContent = JSON.stringify(await r.json(), null, 2); } catch(e){ el.textContent = 'Error: '+e.message }
    }
  </script>
</body></html>`;
}
