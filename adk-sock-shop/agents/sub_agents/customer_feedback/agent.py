"""Search Customer Feedback Agent."""

import json
import os

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import (
    LlmRequest,  # pyright: ignore[reportPrivateImportUsage]
    LlmResponse,  # pyright: ignore[reportPrivateImportUsage]
)
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from . import prompt

_END_OF_EDIT_MARK = "---END-OF-EDIT---"


def _remove_end_of_edit_mark(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> LlmResponse:
    del callback_context  # unused
    if not llm_response.content or not llm_response.content.parts:
        return llm_response
    for idx, part in enumerate(llm_response.content.parts):
        if part.text is None:
            continue
        if _END_OF_EDIT_MARK in part.text:
            del llm_response.content.parts[idx + 1 :]
            part.text = part.text.split(_END_OF_EDIT_MARK, 1)[0]
    return llm_response


def force_string_content(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    del callback_context  # unused
    """
    Ensure every Content in llm_request.contents ends up as a *single* text part,
    so llama.cpp never sees lists/dicts/None.
    """
    new_contents: list[types.Content] = []

    for content in llm_request.contents:
        # If it is already plain text, keep it
        if isinstance(content, str):
            new_contents.append(
                types.Content(role="user", parts=[types.Part(text=content)])
            )
            continue

        # Merge multiple Parts into a single string
        if isinstance(content, types.Content):
            merged_text = "\n".join((p.text or "") for p in content.parts or [])
            new_contents.append(
                types.Content(
                    role=content.role or "user", parts=[types.Part(text=merged_text)]
                )
            )
            continue

        # Fallback: JSON-encode any dict / list / None
        new_contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=json.dumps(content, ensure_ascii=False))],
            )
        )

    # add after new_contents construction
    collapsed: list = []
    for c in new_contents:
        if collapsed and collapsed[-1].role == c.role and c.parts:
            collapsed[-1].parts[0].text += "\n" + (c.parts[0].text or "")
        else:
            collapsed.append(c)
    llm_request.contents = collapsed
    return None  # let ADK proceed normally

from ...tools import create_mcp_toolsets

tools = create_mcp_toolsets(tools_cfg=["mcp/mongodb:find", "mcp/mongodb:count"])

customer_feedback_agent = Agent(
    # Using local model runner with MODEL_RUNNER_URL
    model=LiteLlm(model=f"openai/{os.environ.get('MODEL_RUNNER_MODEL')}", api_base=f"{os.environ.get('MODEL_RUNNER_URL')}"),
    name="customer_feedback_agent",
    instruction=prompt.PROMPT,
    tools=tools, # type: ignore
)
