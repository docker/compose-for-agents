# 🧠 Langchaingo + DuckDuckGo with Model Context Protocol (MCP)

This project demonstrates a **zero-config application** using [Langchaingo] and
the **Model Context Protocol (MCP)** to answer natural language questions by performing
real-time web search via [DuckDuckGo] — all orchestrated with [Docker Compose].

> [!Tip]
> ✨ No configuration needed — run it with a single command.

<p align="center">
  <img src="demo.gif"
       alt="Langchaingo DuckDuckGo Search Demo"
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

### Run the project

```sh
docker compose up
```

No setup, API keys, or additional configuration required.

# 🧠 Inference Options

By default, this project uses [Docker Model Runner] to handle LLM inference locally — no internet
connection or external API key is required.

If you’d prefer to use OpenAI instead:

1. Create a `secret.openai-api-key` file with your OpenAI API key:

    ```plaintext
    sk-...
    ```

2. Restart the project with the OpenAI configuration:

    ```sh
    docker compose down -v
    docker compose -f compose.yaml -f compose.openai.yaml up
    ```

# ❓ What Can It Do?

Ask natural language questions and let Langchaingo + DuckDuckGo Search provide intelligent, real-time answers:

+ “Does Langchaingo support the Model Context Protocol?”
+ “What is the Brave Search API?”
+ “Give me examples of Langchaingo integrations.”

The application uses:

+ A MCP-compatible gateway to route queries to DuckDuckGo Search
+ Langchaingo’s LLM client to embed results into answers
+ An MCP client to call tools, using the [Model Context Protocol's Go SDK].

To **customize the question** asked to the agent, edit the `QUESTION` environment variable in `compose.yaml`.

# 🧱 Project Structure

| **File/Folder**          | **Purpose**                                      |
| ------------------------ | ------------------------------------------------ |
| `compose.yaml`           | launches the DuckDuckGo MCP gateway and app |
| `Dockerfile`             | Builds the Go container                 |
| `main.go`                | Configures the ChatClient with MCP and runs it |
| `tool_duckduck.go`       | Implements the DuckDuckGo tool |

# 🔧 Architecture Overview

```mermaid

flowchart TD
    A[($QUESTION)] --> B[Go App]
    B --> C[Langchaingo ChatClient]
    C -->|uses| M[MCP Client]
    M -->|uses| D[MCP Tool Callback]
    D -->|queries| E[Docker MCP Gateway]
    E -->|calls| F[DuckDuckGo Search API]
    F --> E --> D --> C
    C -->|LLM| H[(Docker Model Runner)]
    H --> C
    C --> G[Final Answer]

```

+ The application loads a question via the `QUESTION` environment variable.
+ MCP is used as a tool in the LLM pipeline.
+ The response is enriched with real-time DuckDuckGo Search results.

# 📎 Credits

+ [Langchaingo]
+ [DuckDuckGo]
+ [Docker Compose]

[DuckDuckGo]: https://duckduckgo.com
[Langchaingo]: https://github.com/tmc/langchaingo
[Model Context Protocol's Go SDK]: https://github.com/modelcontextprotocol/go-sdk/
[Docker Compose]: https://github.com/docker/compose
[Docker Desktop]: https://www.docker.com/products/docker-desktop/
[Docker Engine]: https://docs.docker.com/engine/
[Docker Model Runner]: https://docs.docker.com/ai/model-runner/
[Docker Model Runner requirements]: https://docs.docker.com/ai/model-runner/
[Docker Offload]: https://www.docker.com/products/docker-offload/
