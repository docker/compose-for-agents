# MCP UI with Vercel AI SDK

Start an MCP UI application that uses the [Vercel AI SDK] to provide a chat interface for local models, provided by the Docker Model Runner, with access to MCPs from the [Docker MCP Catalog].

The application will start up with two models loaded (qwen3 and llama3.2), which both support tool calling.  See the [./compose.yaml](./compose.yaml) file for examples of how to add more models.

The application also starts with a connection to the Docker MCP Gateway, which has been configured to provide access to two MCPs (Brave and Wikipedia).  See the [./compose.yaml](./compose.yaml) file for examples of how to provide access to more MCPs.

# Getting Started

### Requirements

+ **[Docker Desktop](https://www.docker.com/products/docker-desktop/) 4.43.0+ or [Docker Engine](https://docs.docker.com/engine/)** installed
+ **A laptop or workstation with a GPU** (e.g., a MacBook) for running open models locally. If you don't have a GPU, you can alternatively use [**Docker Offload**](https://www.docker.com/products/docker-offload).
+ If you're using Docker Engine on Linux or Docker Desktop on Windows, ensure that the [Docker Model Runner requirements](https://docs.docker.com/ai/model-runner/) are met (specifically that GPU support is enabled) and the necessary drivers are installed
+ If you're using Docker Engine on Linux, ensure you have Compose 2.38.1 or later installed

### Configure MCP secrets

This demo uses the Brave MCP, which requires an API key.  You can create a free api key at the [Brave Search api console](https://api-dashboard.search.brave.com/login).

```sh
docker mcp secret set 'brave.api_key=<insert your Brave Search API key here>'
```

### Clone the project repository

```sh
git clone git@github.com:slimslenderslacks/scira-mcp-chat.git
cd scira-mcp-chat
# create a blank .mcp.env for now (will remove this step once cloud has secret support)
touch .mcp.env
```

### Run the project locally

```sh
docker compose up --build
```

Access the MCP UI at [http://localhost:3000](http://localhost:3000).

# What can it do?

Choose one of the two local models loaded by compose.yaml, and request that it do something with either Brave Search, or the Wikipedia tools.  For example:

> do a wikipedia search for articles about Docker and MCP

### Run the project in Docker Cloud

```sh
# only required temporarily to support Cloud secrets
docker mcp secret export brave > .mcp.env

# compose.cloud.yaml still has one small diff from the local one.
docker compose up --build
```

# Project Structure

| File/Folder    | Purpose                                                                   |
| -------------- | ------------------------------------------------------------------------- |
| `compose.yaml`                              | Defines available models and MCPs           |
| `Dockerfile`                                | Builds MCP UI application                                       |
| `Dockerfile.initialize-chat-store-schema`   | Builds a container that initializes a postgres Schema for the app                                         |

# Cleanup

```sh
docker compose down
```

# Credits

- [Vercel AI SDK]
- [Docker MCP Toolkit]
- [Docker MCP Catalog]

[Vercel AI SDK]: https://ai-sdk.dev/docs/introduction
[Docker MCP Toolkit]: https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit/
[Docker MCP Catalog]: https://hub.docker.com/mcp
