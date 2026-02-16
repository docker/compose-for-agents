# 🛡️ CrewAI Research Agent with Pipelock Security Proxy

A CrewAI research agent that fetches web content through
[Pipelock](https://github.com/luckyPipewrench/pipelock), an open-source security proxy
for AI agents. All outbound HTTP traffic is scanned for credential leaks, SSRF attacks,
and prompt injection before the agent sees it.

> [!Tip]
> ✨ No configuration needed. Run it with a single command.

## 🚀 Getting Started

### Requirements

+ **[Docker Desktop] 4.43.0+ or [Docker Engine]** installed.
+ **A laptop or workstation with a GPU** (e.g., a MacBook) for running open models locally. If you
  don't have a GPU, you can alternatively use **[Docker Offload]**.
+ If you're using [Docker Engine] on Linux or [Docker Desktop] on Windows, ensure that the
  [Docker Model Runner requirements] are met (specifically that GPU
  support is enabled) and the necessary drivers are installed.
+ If you're using Docker Engine on Linux, ensure you have [Docker Compose] 2.38.1 or later installed.

### Run the Project

```sh
docker compose up --build
```

The agent starts a research task on "AI agent security best practices." It searches the web using
DuckDuckGo (via MCP), fetches pages through Pipelock's security proxy, and writes a summary of its
findings.

Pipelock scans every outbound request for leaked API keys and credentials (DLP), blocks SSRF
attempts targeting internal networks, and checks fetched content for prompt injection before
returning it to the agent.

## 🧠 Inference Options

By default, this project uses [Docker Model Runner] to handle LLM inference locally. No internet
connection or external API key is required.

If you'd prefer to use OpenAI instead:

1. Create a `secret.openai-api-key` file with your OpenAI API key:

    ```plaintext
    sk-...
    ```

2. Restart the project with the OpenAI configuration:

    ```sh
    docker compose down -v
    docker compose -f compose.yaml -f compose.openai.yaml up
    ```

## 🔒 What Does Pipelock Scan?

The agent's HTTP traffic passes through the Pipelock sidecar, which applies these checks:

+ **DLP (Data Loss Prevention)** -- Blocks requests containing API keys, tokens, AWS credentials,
  private keys, and other secrets. 14 built-in regex patterns.
+ **SSRF Protection** -- Blocks requests targeting private IPs, link-local addresses, and cloud
  metadata endpoints (169.254.169.254).
+ **Prompt Injection Detection** -- Scans fetched HTML/text for common injection patterns before
  the content reaches the agent.
+ **Rate Limiting** -- Per-domain request limits prevent runaway loops.
+ **Data Budgets** -- Per-domain byte limits prevent slow-drip data exfiltration.

All scan results are logged as structured JSON for audit.

## 🧱 Project Structure

| File/Folder | Purpose |
|-------------|---------|
| `compose.yaml` | Service orchestration with network isolation. |
| `compose.openai.yaml` | Override to use OpenAI instead of Docker Model Runner. |
| `pipelock.yaml` | Pipelock security proxy configuration. |
| `Dockerfile` | Builds the CrewAI agent container. |
| `src/agent.py` | Agent definition with secure fetch tool. |

## 🔧 Architecture Overview

```mermaid
flowchart TD
    A[CrewAI Agent] -->|fetch request| P[Pipelock Proxy]
    A -->|MCP tool call| M[MCP Gateway]
    M -->|DuckDuckGo search| I[Internet]
    P -->|DLP + SSRF + injection scan| P
    P -->|allowed requests only| I
    P -->|scanned response| A

    subgraph agent-net [Internal Network]
        A
        P
        M
    end

    subgraph default [External Network]
        I
    end

    P --- default
```

The agent container lives on an **internal-only Docker network** with no direct internet access.
Pipelock bridges the internal and external networks, acting as the sole gateway for outbound HTTP.
The MCP gateway provides tool access (web search) on the internal network.

## 🧹 Cleanup

To stop and remove containers and volumes:

```sh
docker compose down -v
```

## 📎 Credits

+ [Pipelock](https://github.com/luckyPipewrench/pipelock) -- Open-source security proxy for AI
  agents
+ [CrewAI](https://github.com/crewAIInc/crewAI) -- Multi-agent orchestration framework
+ [Docker Model Runner](https://docs.docker.com/model-runner/) -- Local LLM inference

[Docker Desktop]: https://www.docker.com/get-started/
[Docker Engine]: https://docs.docker.com/engine/install/
[Docker Offload]: https://docs.docker.com/desktop/features/offload/
[Docker Model Runner]: https://docs.docker.com/model-runner/
[Docker Model Runner requirements]: https://docs.docker.com/model-runner/
[Docker Compose]: https://docs.docker.com/compose/install/
