"""A2A Proxy Agent Module

This module provides a proxy agent that forwards requests to an A2A (Agent-to-Agent) server.
It acts as a bridge between the ADK framework and external A2A services.
"""
from typing import AsyncGenerator, Optional
import asyncio
import uuid

import httpx
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types

from a2a.client import A2AClient
from a2a.types import AgentCard, MessageSendParams, SendMessageRequest, SendStreamingMessageRequest

class A2AProxyAgent(BaseAgent):
    """Non-LLM agent that proxies calls to an A2A server"""

    # Declare fields as class attributes for Pydantic model
    a2a_url: str
    output_key: Optional[str] = None
    httpx_client: Optional[httpx.AsyncClient] = None
    client: Optional[A2AClient] = None

    def __init__(self, name: str, a2a_url: str, description: str = "", output_key: str = None):
        super().__init__(
            name=name,
            description=description,
            a2a_url=a2a_url,
            output_key=output_key,
            httpx_client=None,
            client=None
        )
    
    async def _initialize_client(self):
        """Initialize A2A client by fetching agent card"""
        if self.client is None:
            self.httpx_client = httpx.AsyncClient()
            
            # Fetch agent card first (optional but recommended)
            try:
                response = await self.httpx_client.get(f"{self.a2a_url}/agent-card")
                agent_card_data = response.json()
                agent_card = AgentCard(**agent_card_data)
                
                # Create client with agent card
                self.client = A2AClient(
                    httpx_client=self.httpx_client,
                    agent_card=agent_card
                )
            except:
                # Fallback to URL-only initialization
                self.client = A2AClient(
                    httpx_client=self.httpx_client,
                    url=self.a2a_url
                )
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Agent execution: forwards directly to A2A"""

        # Initialize client if needed
        await self._initialize_client()

        # Get content to send
        if ctx.user_content and ctx.user_content.parts:
            content_to_send = ctx.user_content.parts[0].text
        else:
            content_to_send = self._get_input_from_state(ctx)

        try:
            # Create the message payload based on the A2A example and your curl test
            message_id = str(uuid.uuid4())
            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': content_to_send}
                    ],
                    'messageId': message_id,
                    'kind': 'message'
                },
                'skill': 'fact_check_answer'
            }

            # Try streaming first, fallback to non-streaming if needed
            streaming_request = SendStreamingMessageRequest(
                id=str(uuid.uuid4()),
                params=MessageSendParams(**send_message_payload)
            )

            # Collect streaming response
            final_result = ""
            try:
                stream_response = self.client.send_message_streaming(streaming_request)

                async for chunk in stream_response:
                    chunk_content = ""

                    # Extract content from A2A streaming response
                    if (hasattr(chunk, 'root') and chunk.root and
                        hasattr(chunk.root, 'result') and chunk.root.result and
                        hasattr(chunk.root.result, 'artifact') and chunk.root.result.artifact):
                        artifact = chunk.root.result.artifact
                        if hasattr(artifact, 'parts') and artifact.parts:
                            for part in artifact.parts:
                                if hasattr(part, 'root') and part.root and hasattr(part.root, 'text') and part.root.text:
                                    chunk_content = str(part.root.text)
                                    break
                                elif hasattr(part, 'text') and part.text:
                                    chunk_content = str(part.text)
                                    break
                    elif hasattr(chunk, 'result') and chunk.result:
                        if hasattr(chunk.result, 'content') and chunk.result.content:
                            chunk_content = str(chunk.result.content)
                        elif hasattr(chunk.result, 'message') and chunk.result.message:
                            if hasattr(chunk.result.message, 'content') and chunk.result.message.content:
                                chunk_content = str(chunk.result.message.content)
                        elif hasattr(chunk.result, 'text') and chunk.result.text:
                            chunk_content = str(chunk.result.text)
                    elif hasattr(chunk, 'content') and chunk.content:
                        chunk_content = str(chunk.content)
                    elif hasattr(chunk, 'text') and chunk.text:
                        chunk_content = str(chunk.text)

                    if chunk_content:
                        final_result += chunk_content

            except Exception as streaming_error:
                # Fallback to non-streaming if streaming fails
                request = SendMessageRequest(
                    id=str(uuid.uuid4()),
                    params=MessageSendParams(**send_message_payload)
                )
                response = await self.client.send_message(request)

                # Handle non-streaming response
                if hasattr(response, 'result') and response.result:
                    if hasattr(response.result, 'content'):
                        final_result = response.result.content
                    elif hasattr(response.result, 'message') and hasattr(response.result.message, 'content'):
                        final_result = response.result.message.content
                    else:
                        final_result = str(response.result)
                else:
                    final_result = str(response)

            # Save to state
            if self.output_key:
                ctx.session.state[self.output_key] = final_result

            # Return result
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=final_result)]
                ),
                actions=EventActions(
                    state_delta={self.output_key: final_result} if self.output_key else {}
                ),
                turn_complete=True
            )
            
        except Exception as e:
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=f"Error calling A2A agent: {str(e)}")]
                ),
                error_message=str(e),
                turn_complete=True
            )

    async def _run_live_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Live (audio/video) mode is not supported for A2A proxy agents"""
        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part(text="A2A proxy agents do not support live audio/video mode")]
            ),
            error_message="Live mode not supported",
            turn_complete=True
        )

    def _get_input_from_state(self, ctx: InvocationContext) -> str:
        """Retrieves input from state for non-first agents in sequence"""
        state = ctx.session.state.to_dict()
        
        # Look for output from previous agent
        for key in reversed(list(state.keys())):
            if key.endswith('_result') or key.endswith('_output'):
                return state[key]
        
        # Fallback: take original user message
        if ctx.session.events:
            for event in ctx.session.events:
                if event.content and event.content.role == "user":
                    return event.content.parts[0].text
        
        return "No input found"
    
    async def cleanup(self):
        """Clean up the httpx client"""
        if self.httpx_client:
            await self.httpx_client.aclose()