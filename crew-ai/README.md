# 🧠 CrewAI Marketing Team Demo

This project showcases an autonomous, multi-agent **virtual marketing team** built with
[CrewAI](https://github.com/joaomdmoura/crewAI). It automates the creation of a high-quality, end-to-end marketing strategy — from research to copywriting — using task delegation, web search, and creative synthesis.

> [!Tip]
> ✨ No configuration needed — run it with a single command.


<p align="center">
  <img src="demo.gif"
       alt="CrewAI marketing agent demo"
       width="500"
       style="border: 1px solid #ccc; border-radius: 8px;" />
</p>

## 🚀 Getting Started

### Requirements

- ✅ [Docker Desktop] **v4.43.0+**

### Run the Project

```sh
docker compose up --build
```

That’s all. The agents will spin up and collaborate through a series of predefined roles and tasks to
deliver a complete marketing strategy for the input project.

# 🧠 Inference Options

By default, this project uses [Docker Model Runner] to handle LLM inference locally — no internet connection or external API key is required.

If you’d prefer to use OpenAI instead:

1. Create a `secret.openai-api-key` file with your OpenAI API key:

```
sk-...
```

2. Restart the project with the OpenAI configuration:

```
docker compose down -v
docker compose -f compose.yaml -f compose.openai.yaml up
```

## ❓ What Can It Do?

Give it a company and a project description — the agents will collaborate to produce a full marketing strategy:

- “Research the market landscape around CrewAI’s automation tools.”
- “Understand the target audience for enterprise AI integrations.”
- “Formulate a high-impact marketing strategy with KPIs and channels.”
- “Propose 5 creative campaigns tailored to tech decision-makers.”
- “Write compelling ad copy for each campaign idea.”

From strategy to storytelling, the team handles it all — autonomously.

You can **customize the tasks** to use your own domain and project description — just edit the inputs in `src/config/inputs.yaml`.


# 👥 Virtual Team Structure

| **Agent**                      | **Role**                       | **Responsibilities**                                                   |
| ------------------------------ | ------------------------------ | ---------------------------------------------------------------------- |
| **Lead Market Analyst**        | 🧠 lead_market_analyst        | Performs in-depth research on the customer, competitors, and audience. |
| **Chief Marketing Strategist** | 🎯 chief_marketing_strategist | Designs the complete marketing strategy using team insights.           |
| **Creative Content Creator**   | ✍️ creative_content_creator  | Writes compelling ad copy based on campaign ideas.                     |
| **Chief Creative Director**    | 👑 chief_creative_director    | Reviews and approves all outputs for alignment and quality.            |


# 🧱 Project Structure

| File/Folder    | Purpose                                                |
| -------------- | ------------------------------------------------------ |
| `compose.yaml` | Defines service orchestration.                         |
| `Dockerfile`   | Builds the container environment.                      |
| `src/config`   | Contains the agent, task definitions, and task inputs. |
| `src/*.py`     | Main program and crew definition.                      |



# 🔧 Architecture Overview

```mermaid
flowchart TD
    subgraph Input
      input[(input.yaml<br/>customer & project)]
    end

    subgraph Agents
      A1[(🧠 Lead Market Analyst)]
      A2[(🎯 Chief Marketing Strategist)]
      A3[✍️ Creative Content Creator]
    end

    subgraph Task
      T1[🔍 Research Task]
      T2[📘 Project Understanding Task]
      T3[(📊 Marketing Strategy Task)]
      T4[(💡 Campaign Idea Task)]
      T5[(📝 Copy Creation Task)]
    end

    subgraph AI Tools
      MCP[(MCP Gateway<br/>DuckDuckGo Search)]
      LLM[(Docker Model Runner<br/>LLM Inference)]
    end

    input --> T1
    input --> T2

    T1 -->|assigned to| A1
    T2 -->|assigned to| A2
    T3 -->|assigned to| A2
    T4 -->|assigned to| A3
    T5 -->|assigned to| A3

    A1 --> MCP
    A2 --> MCP

    A1 --> LLM
    A2 --> LLM
    A3 --> LLM

    T1 --> T3
    T2 --> T3
    T3 --> T4
    T3 --> T5
    T4 --> T5

    T5 --> Output[(📄 Final Deliverables<br/>Copy + Strategy + Campaigns)]
```

- The LangGraph-based agent transforms questions into SQL.
- PostgreSQL is populated from a SQLite dump at runtime.
- All components are fully containerized for plug-and-play usage.


# 🧹 Cleanup

To stop and remove containers and volumes:

```sh
docker compose down -v
```


# 📎 Credits
- [crewAI]
- [DuckDuckGo]
- [Docker Compose]


[crewAI]: https://github.com/crewAIInc/crewAI
[DuckDuckGo]: https://duckduckgo.com
[Docker Compose]: https://github.com/docker/compose
[Docker Desktop]: https://www.docker.com/products/docker-desktop/
[Docker Model Runner]: https://docs.docker.com/ai/model-runner/
