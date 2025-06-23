"""Critic Agent Server"""
import logging
import uvicorn
import click

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from .agent import CriticAgent
from .agent_executor import CriticAgentExecutor


#logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@click.command()
@click.option('--host', default='localhost')
@click.option('--port', default=80)
def main(host, port):
    """Main function"""
    try:
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id='fact_check_answer',
            name='Fact Check and Verify Information',
            description='Acts as a professional investigative journalist to critically analyze and verify information in question-answer pairs. Identifies claims, verifies them against reliable sources, and provides detailed assessments of accuracy.',
            tags=['fact-checking', 'verification', 'journalism', 'critical-thinking'],
            examples=[
                'Can you fact-check this answer about climate change statistics?',
                'Please verify the claims made in this response about historical events.',
                'I need you to critically analyze this answer for accuracy and reliability.'
            ],
        )
        agent_card = AgentCard(
            name='Critic Agent',
            description='A professional investigative journalist agent that excels at critical thinking and verifying information. This agent analyzes question-answer pairs by identifying claims, determining their reliability through external sources, and providing comprehensive assessments of accuracy and trustworthiness.',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=CriticAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=CriticAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        request_handler = DefaultRequestHandler(
            agent_executor=CriticAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )
        uvicorn.run(server.build(), host=host, port=port)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        exit(1)


if __name__ == '__main__':
    main()
