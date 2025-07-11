# Embable Travel Agent Planner

**Tripper** is a travel planning agent that helps you create personalized travel itineraries,
based on your preferences and interests. It uses web search, mapping and integrates with Airbnb.
It demonstrates the power of the [Embabel agent framework](https://www.github.com/embabel/embabel-agent).

# Getting Started

### Requirements

+ **[Docker Desktop](https://www.docker.com/products/docker-desktop/) 4.43.0+ or
  [Docker Engine](https://docs.docker.com/engine/)** installed
+ **A laptop or workstation with a GPU** (e.g., a MacBook) for running open models locally. If you don't have a GPU,
  you can alternatively use [**Docker Offload**](https://www.docker.com/products/docker-offload).
+ If you're using Docker Engine on Linux or Docker Desktop on Windows, ensure that the
  [Docker Model Runner requirements](https://docs.docker.com/ai/model-runner/) are met (specifically that GPU support
  is enabled) and the necessary drivers are installed
+ If you're using Docker Engine on Linux, ensure you have Compose 2.38.1 or later installed

### Clone the project repository

> [!IMPORTANT]
> The compose.yaml file is in the upstream repository. To try out this project, you'll need to clone the upstream repo.

```sh
git clone git@github.com:embabel/travel-agent-planner.git
cd travel-agent-planner
```

### Configure MCP secrets

```sh
docker mcp secret set 'brave.api_key=<insert your Brave Search API key here>'
docker mcp secret set 'google-maps.api_key=<insert your Google Maps API key here>'
docker mcp secret set 'github.personal_access_token=<insert your GitHub  PAT>'
docker mcp secret export brave google-maps github > .mcp.env
```

### Run the project locally

```sh
export OPENAI_API_KEY=your_openai_api_key_here
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
# Set your Brave API key for image search (not yet moved into MCP)
export BRAVE_API_KEY=your_brave_api_key_here

docker compose --profile in-docker up
```

Access the Travel Planner at [http://localhost:8080](http://localhost:8080).

# What can it do?

Use the [Travel Planner](http://localhost:8080) interface to plan a trip.

# Cleanup

```sh
docker compose down
```

# Credits

+ [Embabel Agent Framework]
+ [Docker MCP Toolkit]
+ [Docker MCP Catalog]

[Embabel Agent Framework]: https://github.com/embabel/embabel-agent
[Docker MCP Toolkit]: https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit/
[Docker MCP Catalog]: https://hub.docker.com/mcp
