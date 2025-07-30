import asyncio
import os
import sys

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app
from agno.team import Team
from agno.tools import Toolkit
from agno.tools.mcp import MCPTools
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio
import yaml

# Allow nested event loops
nest_asyncio.apply()


def create_model_from_config(entity_data: dict, entity_id: str) -> OpenAIChat:
    """Create a model instance from entity configuration data."""
    model = entity_data.get("model", {})
    name = model.get("name")
    if not name:
        raise ValueError(
            f"Model name not specified for {entity_id}. Please set 'model.name' in the configuration."
        )
    provider = model.get("provider", "")
    temperature = entity_data.get("temperature")
    return create_model(name, provider, temperature)


def create_model(
    model_name: str, provider: str, temperature: float | None
) -> OpenAIChat:
    """Create a model instance based on the model name and provider."""
    print(
        f"creating model {model_name} with provider {provider} and temperature {temperature}"
    )
    if provider == "docker":
        base_url = os.getenv("MODEL_RUNNER_URL")
        if base_url is None:
            raise ValueError(
                f"MODEL_RUNNER_URL environment variable not set for {model_name}."
            )
        model = OpenAIChat(id=model_name, base_url=base_url, temperature=temperature)
        model.role_map = {
            "system": "system",
            "user": "user",
            "assistant": "assistant",
            "tool": "tool",
            "model": "assistant",
        }
        return model

    if provider == "openai":
        if os.environ.get("OPENAI_API_KEY") is None:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set for OpenAI model"
            )
        return OpenAIChat(model_name, temperature=temperature)

    raise ValueError(f"Unknown agent model provider: {provider}")


async def create_mcp_tools(tools_list: list[str], entity_type: str) -> list[Toolkit]:
    """Create MCP tools from a list of tool names."""
    if len(tools_list) == 0:
        return []

    tool_names = [name.split(":", 1)[1] for name in tools_list]

    gateway_url = os.environ.get("MCPGATEWAY_URL")
    if not gateway_url:
        raise ValueError(
            f"MCPGATEWAY_URL environment variable not set for {entity_type} tools"
        )
    command: str | None = None
    url: str | None = None
    transport: str = ""
    if gateway_url.startswith("http://") or gateway_url.startswith("https://"):
        url = gateway_url
        transport = "streamable-http"
        print(
            f"DEBUG: {entity_type} connecting to MCP gateway via streamable-http {url}"
        )
    else:
        # Assume it's a TCP endpoint
        tcp_endpoint = gateway_url
        transport = "stdio"
        command = f"socat STDIO TCP:{tcp_endpoint}"
        print(
            f"DEBUG: {entity_type} connecting to MCP gateway via STDIO {tcp_endpoint}"
        )
    t = MCPTools(
        command=command,
        url=url,
        transport=transport,  # type: ignore
        include_tools=tool_names,
    )
    mcp_tools = await t.__aenter__()
    return [mcp_tools]


def get_common_config(entity_data: dict) -> dict:
    """Extract common configuration options."""
    return {
        "markdown": entity_data.get("markdown", False),
        "add_datetime_to_instructions": True,
        "debug_mode": True,
    }


async def run_server(config) -> None:
    """Run the playground server."""
    # Create a client session to connect to the MCP server
    agents = []
    agents_by_id = {}
    teams = []
    teams_by_id = {}

    for agent_id, agent_data in config.get("agents", {}).items():
        model = create_model_from_config(agent_data, agent_id)
        common_config = get_common_config(agent_data)

        tools: list[Toolkit] = [
            #            ReasoningTools(think=True, analyze=True)
        ]
        tools_list = agent_data.get("tools", [])
        mcp_tools = await create_mcp_tools(tools_list, "Agent")
        if mcp_tools:
            tools = mcp_tools
        agent = Agent(
            name=agent_data["name"],
            role=agent_data.get("role", ""),
            description=agent_data.get("description"),
            instructions=agent_data.get("instructions"),
            tools=tools,  # type: ignore
            model=model,
            show_tool_calls=True,
            **common_config,
        )
        agents_by_id[agent_id] = agent
        # Append only agents that we want to chat with
        if agent_data.get("chat", True):
            agents.append(agent)

    for team_id, team_data in config.get("teams", {}).items():
        model = create_model_from_config(team_data, team_id)
        common_config = get_common_config(team_data)

        team_agents: list[Agent | Team] = []
        for agent_id in team_data.get("members", []):
            try:
                agent = agents_by_id[agent_id]
            except KeyError:
                raise ValueError(f"Agent {agent_id} not found in agents")
            team_agents.append(agent)

        team_tools: list[Toolkit] = [
            #  ReasoningTools(think=True, analyze=True)
        ]
        tools_list = team_data.get("tools", [])
        mcp_tools = await create_mcp_tools(tools_list, "Team")
        if mcp_tools:
            team_tools = mcp_tools
        team = Team(
            name=team_data.get("name", ""),
            mode=team_data.get("mode", "coordinate"),
            members=team_agents,
            description=team_data.get("description"),
            instructions=team_data.get("instructions"),
            tools=team_tools,  # type: ignore
            model=model,
            # show_members_responses=True,
            # show_tool_calls=True,
            **common_config,
        )
        teams_by_id[team_id] = team
        if team_data.get("chat", True):
            teams.append(team)

    playground = Playground(agents=agents, teams=teams)

    app = playground.get_app()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve the app while keeping the MCPTools context manager alive
    serve_playground_app(host="0.0.0.0", app=app)


def main():
    config_filename = sys.argv[1] if len(sys.argv) > 1 else "/agents.yaml"
    with open(config_filename, "r") as f:
        expanded = os.path.expandvars(f.read())
        config = yaml.safe_load(expanded)

    asyncio.run(run_server(config))


if __name__ == "__main__":
    main()
