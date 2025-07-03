import os

from google.adk.agents.llm_agent import LlmAgent as ADKLlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.lite_llm import LiteLlm

from ..tools.mcp import create_mcp_toolsets
from .agent import ADKBaseAgent, Agent
from .config import AgentType


@Agent.register(AgentType.LLM)
class LlmAgent(Agent):
    def _build_agent(self, sub_agents: list[ADKBaseAgent]) -> ADKBaseAgent:
        tools = create_mcp_toolsets(tools_cfg=self._config.tools or [])
        return ADKLlmAgent(
            model=self._build_model(),
            name=self._config.agent_id,
            description=self._config.description or "",
            instruction=self._config.instructions or "",
            tools=tools,  # type: ignore
            sub_agents=sub_agents,
        )

    def _build_model(self) -> BaseLlm:
        """Builds the LLM model."""
        if not self._config.model:
            raise ValueError(f"LLM agent {self._config.name} does not specify a model")
        provider: str | None
        if isinstance(self._config.model, str):
            provider = "docker"
            name = self._config.model
        else:
            provider = self._config.model.provider
            name = self._config.model.name

        if not name:
            raise ValueError(
                f"LLM agent {self._config.name} does not specify a model name"
            )

        if not provider:
            provider = "docker"

        base_url = None
        api_key: str | None = None
        if provider == "docker":
            api_key = "does_not_matter_but_cannot_be_empty"
            base_url = os.getenv("MODEL_RUNNER_URL")
            if not base_url:
                raise ValueError("MODEL_RUNNER_URL environment variable is not set")
            name = "openai/" + name
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
        else:
            raise ValueError(f"unknown model provider {provider}")
        return LiteLlm(model=name, api_key=api_key, base_url=base_url)
