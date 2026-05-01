from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Uncomment the following line to use an example of a custom tool
# from marketing_posts.tools.custom_tool import MyCustomTool
from pydantic import BaseModel, Field

from .tools import get_tools


class MarketStrategy(BaseModel):
    """Market strategy model"""

    name: str = Field(..., description="Name of the market strategy")
    tactics: List[str] = Field(
        ..., description="List of tactics to be used in the market strategy"
    )
    channels: List[str] = Field(
        ..., description="List of channels to be used in the market strategy"
    )
    KPIs: List[str] = Field(
        ..., description="List of KPIs to be used in the market strategy"
    )


class CampaignIdea(BaseModel):
    """Campaign idea model"""

    name: str = Field(..., description="Name of the campaign idea")
    description: str = Field(..., description="Description of the campaign idea")
    audience: str = Field(..., description="Audience of the campaign idea")
    channel: str = Field(..., description="Channel of the campaign idea")


class CampaignIdeas(BaseModel):
    title: str = Field(..., description="A title for list of ideas")
    ideas: List[CampaignIdea] = Field(..., description="List of campaign ideas")


class Copy(BaseModel):
    """Copy model"""

    title: str = Field(..., description="Title of the copy")
    body: str = Field(..., description="Body of the copy")


class Copies(BaseModel):
    """Marketing copy collection model"""

    title: str = Field(..., description="Title for the set of marketing copies")
    copies: List[Copy] = Field(..., description="List of marketing copies")


@CrewBase
class MarketingPostsCrew:
    """MarketingPosts crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def lead_market_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_market_analyst"],  # type: ignore
            tools=get_tools(),
            verbose=True,
        )

    @agent
    def chief_marketing_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["chief_marketing_strategist"],  # type: ignore
            tools=get_tools(),
            verbose=True,
        )

    @agent
    def creative_content_creator(self) -> Agent:
        return Agent(
            config=self.agents_config["creative_content_creator"],  # type: ignore
            verbose=True,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],  # type: ignore
            agent=self.lead_market_analyst(),
        )

    @task
    def project_understanding_task(self) -> Task:
        return Task(
            config=self.tasks_config["project_understanding_task"],  # type: ignore
            agent=self.chief_marketing_strategist(),
        )

    @task
    def marketing_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config["marketing_strategy_task"],  # type: ignore
            agent=self.chief_marketing_strategist(),
            output_json=MarketStrategy,
        )

    @task
    def campaign_idea_task(self) -> Task:
        return Task(
            config=self.tasks_config["campaign_idea_task"],  # type: ignore
            agent=self.creative_content_creator(),
            output_json=CampaignIdeas,
        )

    @task
    def copy_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config["copy_creation_task"],  # type: ignore
            agent=self.creative_content_creator(),
            context=[self.marketing_strategy_task(), self.campaign_idea_task()],
            output_json=Copies,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MarketingPosts crew"""
        return Crew(
            agents=self.agents,  # type: ignore - Automatically created by the @agent decorator
            tasks=self.tasks,  # type: ignore - Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
