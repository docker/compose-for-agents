"""
Multi-agent research team using AG2 (formerly AutoGen) with Gradio browser UI.

Open http://localhost:7860 after starting with docker compose up --build.

Three agents collaborate under GroupChat with LLM-driven speaker selection:
  researcher  -- searches the web via MCP DuckDuckGo
  analyst     -- critiques and validates research findings
  writer      -- synthesises the final Markdown report
"""
import asyncio
import os
from collections.abc import AsyncGenerator

import gradio as gr
from mcp import ClientSession
from mcp.client.sse import sse_client

from autogen import ConversableAgent, GroupChat, GroupChatManager, LLMConfig
from autogen.mcp import create_toolkit

MCP_SERVER_URL = os.environ["MCP_SERVER_URL"]
MODEL_BASE_URL = os.environ["MODEL_BASE_URL"]
MODEL_NAME = os.environ["MODEL_NAME"]
API_KEY = os.environ.get("OPENAI_API_KEY", "cannot_be_empty")

llm_config = LLMConfig(
    {"model": MODEL_NAME, "base_url": MODEL_BASE_URL, "api_key": API_KEY},
    temperature=0.3,
)


async def research_topic(message: str, history: list) -> AsyncGenerator[str, None]:
    """Run a GroupChat research session and stream each agent reply to Gradio."""
    async with (
        sse_client(MCP_SERVER_URL, timeout=60) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        toolkit = await create_toolkit(session=session)

        researcher = ConversableAgent(
            name="researcher",
            system_message=(
                "You are a research specialist. Search the web for accurate, up-to-date "
                "information on the assigned topic. Perform at least 3 focused searches. "
                "Summarise findings clearly and cite sources."
            ),
            llm_config=llm_config,
        )
        analyst = ConversableAgent(
            name="analyst",
            system_message=(
                "You are a critical analyst. Review the researcher's findings. "
                "Identify gaps, contradictions, and areas needing deeper investigation. "
                "Ask the researcher for follow-up searches when needed."
            ),
            llm_config=llm_config,
        )
        writer = ConversableAgent(
            name="writer",
            system_message=(
                "You are a technical writer. Once research and analysis are complete, "
                "produce a well-structured Markdown report with:\n"
                "## Executive Summary\n## Key Findings\n## Conclusion\n"
                "End your final message with TERMINATE."
            ),
            llm_config=llm_config,
            is_termination_msg=lambda msg: "TERMINATE" in (msg.get("content") or ""),
        )

        # Register all MCP tools on the researcher (schema for LLM + callable for execution)
        toolkit.register_for_llm(researcher)
        toolkit.register_for_execution(researcher)

        groupchat = GroupChat(
            agents=[researcher, analyst, writer],
            messages=[],
            max_round=12,
            speaker_selection_method="auto",
        )
        manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

        async def run() -> None:
            await researcher.a_initiate_chat(
                manager,
                message=f"Research the following topic thoroughly: {message}",
            )

        task = asyncio.create_task(run())

        # Stream messages as they appear in groupchat.messages.
        # a_initiate_chat yields control at every LLM await point, allowing
        # this polling loop to observe intermediate state without threading.
        accumulated: list[str] = []
        last_count = 0

        while not task.done() or last_count < len(groupchat.messages):
            current = list(groupchat.messages)
            if len(current) > last_count:
                for msg in current[last_count:]:
                    speaker = msg.get("name") or msg.get("role", "agent")
                    content = (msg.get("content") or "").strip()
                    if content and speaker not in ("user", "chat_manager"):
                        accumulated.append(f"**{speaker}:** {content}")
                        yield "\n\n---\n\n".join(accumulated)
                last_count = len(current)
            await asyncio.sleep(0.3)

        try:
            await task
        except Exception as exc:
            accumulated.append(f"**error:** {exc}")
            yield "\n\n---\n\n".join(accumulated)


demo = gr.ChatInterface(
    fn=research_topic,
    title="AG2 Multi-Agent Research Team",
    description=(
        "Enter a research topic. Three AG2 agents (researcher, analyst, writer) collaborate "
        "using DuckDuckGo via MCP. Speaker order is determined dynamically by the LLM."
    ),
    examples=[
        "Latest developments in AI agent frameworks in 2025",
        "How does quantum computing affect modern cryptography?",
        "What are the environmental impacts of large language models?",
    ],
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
