"""Research agent that fetches web content through Pipelock security proxy."""

import os
from typing import Optional

import requests
from crewai import Agent, Crew, Task
from crewai.tools import tool
from crewai_tools import MCPServerAdapter


PIPELOCK_FETCH_URL = os.environ.get("PIPELOCK_FETCH_URL", "http://pipelock:8888/fetch")


@tool
def fetch_url(url: str) -> str:
    """Fetch a web page through the Pipelock security proxy.

    Pipelock scans the request for credential leaks and SSRF attempts,
    then scans the response for prompt injection before returning content.

    Args:
        url: The URL to fetch.

    Returns:
        The page content, or an error message if blocked.
    """
    try:
        resp = requests.get(
            PIPELOCK_FETCH_URL,
            params={"url": url},
            headers={"X-Pipelock-Agent": "crewai-research"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("blocked"):
            return f"BLOCKED by Pipelock: {data.get('block_reason', 'unknown')}"
        return data.get("content", "No content returned")
    except (requests.RequestException, ValueError) as e:
        return f"Fetch error: {e}"


_mcp_server: Optional[MCPServerAdapter] = None


def _get_mcp_tools() -> list:
    """Connect to MCP gateway and return available tools."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServerAdapter(dict(url=os.environ["MCP_SERVER_URL"]))
        print(f"Available MCP tools: {[t.name for t in _mcp_server.tools]}")
    return _mcp_server.tools


def run() -> None:
    """Run the research agent crew."""
    mcp_tools = _get_mcp_tools()

    researcher = Agent(
        role="Security-Aware Researcher",
        goal="Research topics using web search and fetch, with all traffic "
             "scanned by Pipelock for credential leaks and injection attacks",
        backstory=(
            "You are a research analyst with access to web search (via MCP) "
            "and a secure web fetcher (via Pipelock proxy). All your network "
            "traffic is monitored for security threats. Use the search tool "
            "to find relevant URLs, then use fetch_url to read their content."
        ),
        tools=[fetch_url, *mcp_tools],
        verbose=True,
    )

    research_task = Task(
        description=(
            "Research the topic of 'AI agent security best practices' using "
            "web search and fetch. Find at least 2 relevant sources, fetch "
            "their content, and write a brief summary of key findings."
        ),
        expected_output=(
            "A short summary (3-5 paragraphs) of AI agent security best "
            "practices, citing the sources you found."
        ),
        agent=researcher,
    )

    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=True,
    )

    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("RESEARCH RESULTS")
    print("=" * 60)
    print(result)
