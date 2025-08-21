import asyncio
import os

from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.sse import sse_client

base_url = os.getenv("OPENAI_API_BASE_URL")
model = os.getenv("MODEL_NAME")
mcp_server_url = os.getenv("MCP_SERVER_URL")
api_key = os.getenv("OPENAI_API_KEY", "does_not_matter")

system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.

For example, for PostgreSQL, you can use the following query to get the tables:

SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

And to retrieve all columns of a specific table, you can use:
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'your_table_name';

""".format(
    dialect=os.getenv("DATABASE_DIALECT"),
    top_k=5,
)


async def main():
    if mcp_server_url is None:
        raise ValueError("Please set the MCP_SERVER_URL environment variable.")

    llm = init_chat_model(
        model, model_provider="openai", api_key=api_key, base_url=base_url
    )
    async with sse_client(
        url=mcp_server_url,
        timeout=60,
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            print(f"MCP tools loaded: {tools}")
            agent = create_react_agent(
                llm,
                tools=tools,
                prompt=system_prompt,
            )

            question = os.getenv("QUESTION")
            if not question:
                raise ValueError(
                    "Please set the QUESTION environment variable with your question."
                )

            async for step in agent.astream(
                {"messages": [{"role": "user", "content": question}]},
                stream_mode="values",
            ):
                step["messages"][-1].pretty_print()


asyncio.run(main())
