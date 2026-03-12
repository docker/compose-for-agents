"""Unit tests for the AG2 research team agent — no LLM calls, no network."""
import os

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("MODEL_BASE_URL", "https://api.openai.com/v1")
os.environ.setdefault("MODEL_NAME", "gpt-4o-mini")
os.environ.setdefault("MCP_SERVER_URL", "http://localhost:8811/sse")

from autogen import ConversableAgent, GroupChat, GroupChatManager, LLMConfig


def build_test_llm_config() -> LLMConfig:
    return LLMConfig(
        {"model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1", "api_key": "test"}
    )


def test_agents_instantiate() -> None:
    llm = build_test_llm_config()
    researcher = ConversableAgent(name="researcher", system_message="test", llm_config=llm)
    analyst = ConversableAgent(name="analyst", system_message="test", llm_config=llm)
    writer = ConversableAgent(
        name="writer",
        system_message="test",
        llm_config=llm,
        is_termination_msg=lambda m: "TERMINATE" in (m.get("content") or ""),
    )
    assert researcher.name == "researcher"
    assert analyst.name == "analyst"
    assert writer.name == "writer"


def test_group_chat_setup() -> None:
    llm = build_test_llm_config()
    agents = [
        ConversableAgent(name=f"agent_{i}", system_message="test", llm_config=llm)
        for i in range(3)
    ]
    gc = GroupChat(
        agents=agents,
        messages=[],
        max_round=12,
        speaker_selection_method="auto",
    )
    manager = GroupChatManager(groupchat=gc, llm_config=llm)
    assert len(gc.agents) == 3
    assert gc.max_round == 12
    assert gc.speaker_selection_method == "auto"
    assert manager.name == "chat_manager"


def test_termination_condition() -> None:
    llm = build_test_llm_config()
    writer = ConversableAgent(
        name="writer",
        system_message="test",
        llm_config=llm,
        is_termination_msg=lambda m: "TERMINATE" in (m.get("content") or ""),
    )
    assert writer._is_termination_msg({"content": "Great report. TERMINATE"}) is True
    assert writer._is_termination_msg({"content": "Still working..."}) is False
    assert writer._is_termination_msg({"content": ""}) is False


def test_llm_config_model_name() -> None:
    llm = build_test_llm_config()
    agent = ConversableAgent(name="test_agent", system_message="test", llm_config=llm)
    assert agent.llm_config["config_list"][0]["model"] == "gpt-4o-mini"
