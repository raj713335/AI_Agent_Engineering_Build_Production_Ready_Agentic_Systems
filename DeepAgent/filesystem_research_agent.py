import os
from typing import Literal

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
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

Use files as a scratchpad: write notes to /notes.md and drafts to /draft.md files \n
When you revise text, prefer edit_file instead of rewriting the whole file. 

"""

agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions,
    backend=FilesystemBackend(root_dir=".", virtual_mode=True)
)

results = agent.invoke({
    "messages": [
        {"role": "user",
         "content": "Create and /notes.md with 10 bullet points on the topic of blackhole ?, call the internet_search tool to get the latest information "}
    ]
})

print(results["messages"][-1].content)
