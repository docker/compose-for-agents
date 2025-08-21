# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Reviser agent for correcting inaccuracies based on verified findings."""

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


reviser_agent = Agent(
    # OPENAI_MODEL_NAME is set by entrypoint.sh with the model name
    model=LiteLlm(model=os.environ.get("OPENAI_MODEL_NAME", "")),
    name="reviser_agent",
    instruction=prompt.REVISER_PROMPT,
    before_model_callback=force_string_content,
    after_model_callback=_remove_end_of_edit_mark,
)
