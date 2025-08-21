"""Agent for reviewing new suppliers before adding them to the Sock Store."""

from google.adk.agents import SequentialAgent

from .sub_agents.reddit_researcher import reddit_researcher_agent
from .sub_agents.customer_feedback import customer_feedback_agent
from .sub_agents.catalogue import catalog_agent

new_supplier_agent = SequentialAgent(
    name="new_supplier_agent",
    description=
        """
        Supplier Intake Agent
        """,
    sub_agents=[reddit_researcher_agent, customer_feedback_agent, catalog_agent],
)

root_agent = new_supplier_agent
