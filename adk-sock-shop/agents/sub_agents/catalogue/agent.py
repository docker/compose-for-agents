"""Catalogue Agent."""

import json
import os
import requests
from typing import Dict, Any, List

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import (
    LlmRequest,  # pyright: ignore[reportPrivateImportUsage]
    LlmResponse,  # pyright: ignore[reportPrivateImportUsage]
)
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from . import prompt
from ...tools import create_mcp_toolsets


def add_to_catalog(name: str, description: str, imageUrl: List[str], price: float, count: int, tag: List[str]) -> Dict[str, Any]:
    """Add a new product to the catalog via HTTP POST."""
    payload = {
        "name": name,
        "description": description,
        "imageUrl": imageUrl,
        "price": price,
        "count": count,
        "tag": tag
    }
    
    try:
        response = requests.post(
            "http://catalogue/catalogue",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return {
            "success": True,
            "message": f"Product '{name}' added successfully to catalog",
            "status_code": response.status_code,
            "response_data": response.json() if response.content else {}
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"Failed to add product to catalog: {str(e)}",
            "error": str(e)
        }

api_base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
api_base_model = os.environ.get('AI_DEFAULT_MODEL', 'openai/gpt-4')

catalog_agent = Agent(
        name="catalog_agent",
        model=LiteLlm(model=f"{api_base_model}", api_base=f"{api_base_url}", api_key=os.environ.get('OPENAI_API_KEY')),
        #model=LiteLlm(model=f"openai/{os.environ.get('MODEL_RUNNER_MODEL')}", api_base=f"{os.environ.get('MODEL_RUNNER_URL')}"),
        instruction = prompt.PROMPT,
        tools = create_mcp_toolsets(tools_cfg=["mcp/resend:send-email", "mcp/curl:curl"]),  # type: ignore
        )
