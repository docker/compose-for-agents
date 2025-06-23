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

from google.adk.agents import SequentialAgent
from .proxy import A2AProxyAgent

# Create A2A proxy agents
critic_agent = A2AProxyAgent(
    name="critic",
    a2a_url="http://critic-agent-a2a:80",
    description="Evaluates LLM responses for accuracy via A2A",
    output_key="critic_result"
)

# reviser_agent = A2AProxyAgent(
#     name="reviser",
#     a2a_url="http://reviser-service:8080",
#     description="Revises content based on critic feedback via A2A",
#     output_key="final_result"
# )

llm_auditor = SequentialAgent(
    name='llm_auditor',
    description=(
        'Evaluates LLM-generated answers, verifies actual accuracy using the'
        ' web, and refines the response to ensure alignment with real-world'
        ' knowledge.'
    ),
    sub_agents=[critic_agent],
)

root_agent = llm_auditor
