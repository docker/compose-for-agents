"""Supplier Intake Agent."""

import logging
import os

import litellm

from . import agent

# Set default OPENAI_API_KEY if not already set
if "OPENAI_API_KEY" not in os.environ:
    api_key_file = "/run/secrets/openai-api-key"
    if os.path.exists(api_key_file):
        try:
            with open(api_key_file, 'r') as f:
                api_key = f.read().strip()
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
                    logging.info(f"OPENAI_API_KEY set from file: {api_key}")
        except Exception as e:
            pass  # Silently ignore file read errors
else:
    logging.info(f"OPENAI_API_KEY already set in environment")

# Set the base URL for the OpenAI API to the Docker Model Runner URL
os.environ["OTEL_SDK_DISABLED"] = "true"

# Enable logging with reduced verbosity
logging.basicConfig(
    level=logging.INFO,  # Less verbose than DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,  # override ADK defaults
)
logging.getLogger("opentelemetry").setLevel(logging.ERROR)
logging.getLogger("google.adk").setLevel(logging.INFO)
logging.getLogger("LiteLLM").setLevel(logging.INFO)  # Much less verbose
logging.getLogger("litellm").setLevel(logging.INFO)  # Also reduce this
logging.getLogger("httpx").setLevel(logging.WARNING)  # Reduce HTTP logs
logging.getLogger("httpcore").setLevel(logging.WARNING)  # Reduce HTTP core logs
litellm.set_verbose = False  # Disable raw HTTP logs # type: ignore

__all__ = ["agent"]
