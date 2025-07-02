import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .sub_agents import bob_agent, cerebras_agent

root_agent = Agent(
    model=LiteLlm(
        model=f"openai/{os.environ.get('DEVDUCK_CHAT_MODEL')}",
        api_base=os.environ.get("DEVDUCK_BASE_URL"),
        api_key="tada",
        temperature=0.0,
    ),
    name=os.environ.get("DEVDUCK_AGENT_NAME"),
    description=os.environ.get("DEVDUCK_AGENT_DESCRIPTION"),
    instruction=os.environ.get("DEVDUCK_AGENT_INSTRUCTION"),
    sub_agents=[cerebras_agent, bob_agent],
)
