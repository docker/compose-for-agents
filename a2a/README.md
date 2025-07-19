# 🧠 A2A Multi-Agent Fact Checker

This project demonstrates a **collaborative multi-agent system** built with the **Agent2Agent SDK** ([A2A])
and [OpenAI](https://platform.openai.com/api-keys), where a top-level Auditor agent coordinates the workflow
to verify facts. The Critic agent gathers evidence via live internet searches using **DuckDuckGo** through
the Model Context Protocol (**MCP**), while the Reviser agent analyzes and refines the conclusion using
internal reasoning alone. The system showcases how agents with distinct roles and tools can
**collaborate under orchestration**.

> [!Tip]
> ✨ No configuration needed — run it with a single command.

<p align="center">
  <img src="demo.gif"
       alt="A2A Multi-Agent Fact Check Demo"
       width="500"
       style="border: 1px solid #ccc; border-radius: 8px;" />
</p>

# 🚀 Getting Started

### Requirements

+ **[Docker Desktop] 4.43.0+ or [Docker Engine]** installed.
+ **A laptop or workstation with a GPU** (e.g., a MacBook) for running open models locally. If you
  don't have a GPU, you can alternatively use **[Docker Offload]**.
+ If you're using [Docker Engine] on Linux or [Docker Desktop] on Windows, ensure that the
  [Docker Model Runner requirements] are met (specifically that GPU
  support is enabled) and the necessary drivers are installed.
+ If you're using Docker Engine on Linux, ensure you have [Docker Compose] 2.38.1 or later installed.
+ An [OpenAI API Key](https://platform.openai.com/api-keys) 🔑.

### Run the project

Create a `secret.openai-api-key` file with your OpenAI API key:

```plaintext
sk-...
```

Then run:

```sh
docker compose up --build
```

Everything runs from the container. Open `http://localhost:8080` in your browser and then chat with
the agents.

# 🧠 Inference Options

By default, this project uses [OpenAI](https://platform.openai.com) to handle LLM inference. If you'd prefer
to use a local LLM instead, run:

```sh
docker compose -f compose.dmr.yaml up
```

Using [**Docker Offload**](https://www.docker.com/products/docker-offload) with GPU support, you can run the
same demo with a larger model that takes advantage of a more powerful GPU on the remote instance:

```sh
docker compose -f compose.dmr.yaml -f compose.offload.yaml up --build
```

# ❓ What Can It Do?

This system performs multi-agent fact verification, coordinated by an **Auditor**:

+ 🧑‍⚖️ **Auditor**:
  * Orchestrates the process from input to verdict.
  * Delegates tasks to Critic and Reviser agents.
+ 🧠 **Critic**:
  * Uses DuckDuckGo via MCP to gather real-time external evidence.
+ ✍️ **Reviser**:
  * Refines and verifies the Critic’s conclusions using only reasoning.

**🧠 All agents use the Docker Model Runner for LLM-based inference.**

Example question:

> “Is the universe infinite?"

# 🧱 Project Structure

| **File/Folder** | **Purpose**                             |
| --------------- | --------------------------------------- |
| `compose.yaml`  | Launches app and MCP DuckDuckGo Gateway |
| `Dockerfile`    | Builds the agent container              |
| `src/AgentKit`  | Agent runtime                           |
| `agents/*.yaml` | Agent definitions                       |

# 🔧 Architecture Overview

```mermaid

flowchart TD
    input[📝 User Question] --> auditor[🧑‍⚖️ Auditor Sequential Agent]
    auditor --> critic[🧠 Critic Agent]
    critic -->|uses| mcp[MCP Gateway<br/>DuckDuckGo Search]
    mcp --> duck[🌐 DuckDuckGo API]
    duck --> mcp --> critic
    critic --> reviser[(✍️ Reviser Agent<br/>No tools)]
    auditor --> reviser
    reviser --> auditor
    auditor --> result[✅ Final Answer]

    critic -->|inference| model[(🧠 Docker Model Runner<br/>LLM)]
    reviser -->|inference| model

    subgraph Infra
      mcp
      model
    end

```

+ The Auditor is a Sequential Agent, it coordinates Critic and Reviser agents to verify user-provided claims.
+ The Critic agent performs live web searches through DuckDuckGo using an MCP-compatible gateway.
+ The Reviser agent refines the Critic’s conclusions using internal reasoning alone.
+ All agents run inference through a Docker-hosted Model Runner, enabling fully containerized LLM reasoning.

# 🤝 Agent Roles

| **Agent**   | **Tools Used**        | **Role Description**                                                         |
| ----------- | --------------------- | ---------------------------------------------------------------------------- |
| **Auditor** | ❌ None               | Coordinates the entire fact-checking workflow and delivers the final answer. |
| **Critic**  | ✅ DuckDuckGo via MCP | Gathers evidence to support or refute the claim                              |
| **Reviser** | ❌ None               | Refines and finalizes the answer without external input                      |

# 🧹 Cleanup

To stop and remove containers and volumes:

```sh
docker compose down -v
```

# 📎 Credits

+ [A2A]
+ [DuckDuckGo]
+ [Docker Compose]

[A2A]: https://github.com/a2aproject/a2a-python
[DuckDuckGo]: https://duckduckgo.com
[Docker Compose]: https://github.com/docker/compose
[Docker Desktop]: https://www.docker.com/products/docker-desktop/
[Docker Engine]: https://docs.docker.com/engine/
[Docker Model Runner requirements]: https://docs.docker.com/ai/model-runner/
[Docker Offload]: https://www.docker.com/products/docker-offload/
