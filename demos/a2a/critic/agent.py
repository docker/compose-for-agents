"""Critic agent for identifying and verifying statements using search tools."""

import os
from typing import Any, AsyncIterable
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from . import prompt
from .tools import create_mcp_toolsets

tools = create_mcp_toolsets(tools_cfg=["mcp/duckduckgo:search"])

critic_agent = Agent(
    model=LiteLlm(model=f"openai/{os.environ.get('DOCKER-MODEL-RUNNER_MODEL')}"),
    name='critic_agent',
    instruction=prompt.CRITIC_PROMPT,
    tools=tools,
)

class CriticAgent:
    """CriticAgent"""
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._agent = critic_agent
        self._user_id = 'critic_remote_agent'
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def get_processing_message(self) -> str:
        """Get processing message"""
        return 'Processing the request...'

    async def stream(self, query, session_id) -> AsyncIterable[dict[str, Any]]:
        """Stream"""
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        content = types.Content(
            role='user', parts=[types.Part.from_text(text=query)]
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )

        accumulated_response = ""
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response():
                response = ''
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    response = '\n'.join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif (
                    event.content
                    and event.content.parts
                    and any(p.function_response for p in event.content.parts)
                ):
                    # Find the first part with function_response
                    for p in event.content.parts:
                        if p.function_response:
                            response = p.function_response.model_dump()
                            break

                # Use accumulated response if available, otherwise use final response
                final_content = accumulated_response if accumulated_response else response
                yield {
                    'is_task_complete': True,
                    'content': final_content,
                }
            else:
                # Handle streaming content - accumulate partial responses
                if (
                    event.content
                    and event.content.parts
                ):
                    for part in event.content.parts:
                        if part.text:
                            accumulated_response += part.text

                yield {
                    'is_task_complete': False,
                    'updates': self.get_processing_message(),
                }
