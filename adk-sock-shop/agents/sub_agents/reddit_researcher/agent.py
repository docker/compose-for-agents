"""Reddit Researcher Agent"""

import os
import logging

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from . import prompt
from ...tools import create_mcp_toolsets

tools = create_mcp_toolsets(tools_cfg=["mcp/brave:brave_web_search"])
api_base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
api_base_model = os.environ.get('AI_DEFAULT_MODEL', 'openai/gpt-4')

logging.info(f"Reddit Research: Use model {api_base_model} and url {api_base_url}")

reddit_researcher_agent = Agent(
    # Using local model runner with MODEL_RUNNER_URL
    #model=LiteLlm(model=f"openai/{os.environ.get('MODEL_RUNNER_MODEL')}", api_base=f"{os.environ.get('MODEL_RUNNER_URL')}"),
    model=LiteLlm(model=f"{api_base_model}", api_base=f"{api_base_url}", api_key=os.environ.get('OPENAI_API_KEY')),
    name="reddit_researcher_agent",
    instruction=prompt.PROMPT,
    tools=tools,  # type: ignore
)
