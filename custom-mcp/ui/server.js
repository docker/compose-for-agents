import express from 'express';
import fetch from 'node-fetch';

const app = express();
const PORT = process.env.PORT || 8080;
const GATEWAY_URL = process.env.MCP_GATEWAY_URL || 'http://mcp-gateway:8811';

app.use(express.static('public'));

app.get('/api/health', async (req, res) => {
  try {
    const r = await fetch(`${GATEWAY_URL}/health`);
    const text = await r.text();
    res.status(r.status).type('text/plain').send(text);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/config', (req, res) => {
  res.json({ gateway: GATEWAY_URL, servers: process.env.MCP_SERVERS?.split(',') || [] });
});

app.listen(PORT, () => {
  console.log(`UI listening on http://localhost:${PORT}`);
});
