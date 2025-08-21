# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Build and Run

```bash
# Build and push multi-platform image (requires hydrobuild builder)
make build-adk-image
```

### Development Tools

```bash
# Type checking
pyright

# Code formatting and linting
ruff check
ruff format
```

### Testing and Development

- Access the web interface at <http://localhost:8080> after running `docker compose up --build`
- Use Google Cloud Run deployment with `compose.gcloudrun.yaml` for cloud deployment

## Architecture Overview

This is an **ADK (Agent Development Kit) multi-agent fact-checking system** with three coordinated agents:

### Agent Hierarchy

- **Root Agent**: `llm_auditor` (SequentialAgent) at `agents/agent.py:22`
  + Orchestrates the entire fact-checking workflow
  + Coordinates between Critic and Reviser agents sequentially
  
- **Critic Agent**: `agents/sub_agents/critic/agent.py:27`
  + Has access to DuckDuckGo search via MCP (Model Context Protocol)
  + Gathers external evidence to support or refute claims
  + Uses `mcp/duckduckgo:search` toolset
  
- **Reviser Agent**: `agents/sub_agents/reviser/agent.py:97`
  + No external tools - pure reasoning agent
  + Refines conclusions based on Critic's findings
  + Uses content processing callbacks for model compatibility

### Agent Communication Pattern

1. User submits question → Auditor
2. Auditor → Critic (with search tools)
3. Critic gathers evidence → Auditor
4. Auditor → Reviser (reasoning only)
5. Reviser refines conclusion → Auditor
6. Auditor delivers final answer

### Special Implementation Notes

- Reviser agent uses content preprocessing callbacks (`force_string_content`, `_remove_end_of_edit_mark`) for model compatibility
- MCP tools are configured via `create_mcp_toolsets()` in critic agent
- All agents use LiteLLM for model abstraction with OpenAI format

### Generating a compose.yaml file

- To add models and gateways to an existing compose.yaml file, you should figure out which model you
  want to use, and which mcp servers are needed.
- Create a service entry like the following:

    ```yaml
    mcp-gateway:
      image: docker/mcp-gateway:latest
      use_api_socket: true
      command:
        - --transport=sse
        - --servers=server1,server2,server3
        - --config=/mcp_config
        - --secrets=docker-desktop:/run/secrets/mcp_secret
      secrets:
        - mcp_secret
    ```

    but replace the servers value with a comma-separate list of the MCP servers that you want to use.

- Also, if there is no top-level `secrets` entry with a `mcp_secret` entry then add one. It should look
  like:

    ```yaml
    secrets:
      mcp_secret:
        file: ./.mcp.env
    ```

  and remind that the user that Docker offload will require secrets to be stored in a local file named .mcp.env

- Whenever a model is needed, add a toplevel entry in the compose.yaml file with the name of the
  model.  It should look like:
  
    ```yaml
    models:
      <model_name>:
        model: <model_image_ref>
    ```

    but replace the <model_name> with whatever model the user wants to use.
    If the user wnts the model_name qwen3 then the model_image_ref should be ai/qwen3:14B-Q6_K
- Whenever a model is added, the user must specify what service needs the model.
    Add a new entry to that service's definition with the following content.

    ```yaml
    models:
      <model_name>:
        endpoint_var: MODEL_RUNNER_URL
        model_var: MODEL_RUNNER_MODEL
    ```

    If it's unclear which service needs this definition then ask. Always add the model to just the
    service definition that needs it.
