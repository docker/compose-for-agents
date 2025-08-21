import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

bob_agent = Agent(
    model=LiteLlm(
        model=f"openai/{os.environ.get('BOB_CHAT_MODEL')}",
        api_base=os.environ.get("BOB_BASE_URL"),
        api_key="tada",
        temperature=0.0,
    ),
    name=os.environ.get("BOB_AGENT_NAME"),
    description=os.environ.get("BOB_AGENT_DESCRIPTION"),
    instruction=os.environ.get("BOB_AGENT_INSTRUCTION"),
)
