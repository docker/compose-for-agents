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

"""LLM Auditor for verifying & refining LLM-generated answers using the web."""

import logging

import litellm

from . import agent

# Enable logging with reduced verbosity
logging.basicConfig(
    level=logging.INFO,  # Less verbose than DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,  # override ADK defaults
)
logging.getLogger("google.adk").setLevel(logging.INFO)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)  # Much less verbose
logging.getLogger("litellm").setLevel(logging.WARNING)  # Also reduce this
logging.getLogger("httpx").setLevel(logging.WARNING)  # Reduce HTTP logs
logging.getLogger("httpcore").setLevel(logging.WARNING)  # Reduce HTTP core logs
litellm.set_verbose = False  # Disable raw HTTP logs # type: ignore

__all__ = ["agent"]
