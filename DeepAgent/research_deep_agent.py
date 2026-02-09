import os
from typing import Literal

from deepagents import create_deep_agent
from tavily import TavilyClient
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
):
    """Return a web search"""

    print(query, topic, max_results)

    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic
    )


model = init_chat_model("openai:gpt-4.1-mini")

research_instructions = """You are a expert researcher.
Your job: gather information and write a short, structured report.

Primary research tool:  `internet_search`

## Tool: internet_search
- Use this tool to search internet for query
- max_results controls how many results you fetch
- topic can be general/news/finance

"""

agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions
)


for i in range(1, 25):

    print(f"Iteration Number {i}")
    results = agent.invoke({
        "messages": [
            {"role": "user",
             "content": "What is a blackhole ?, call the internet_search tool to get the latest information "}
        ]
    })

    print(results["messages"][-1].content)
    print(" ")
