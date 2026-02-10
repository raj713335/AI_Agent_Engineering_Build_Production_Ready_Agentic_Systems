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


researcher_subagent = {
    "name": "researcher",
    "description": "Find sources and produces structured research notes.",
    "system_prompt": (
        "You are a research specialist. You use internet_search. \n"
        "Return (1) key findings, (2) sources, (3) uncertainties."
    ),
    "tools": [internet_search],
}

writer_subagent = {
    "name": "writer",
    "description": "Turn notes into a clean Markdown report.",
    "system_prompt": (
        "You are a technical writer \n"
        "Write a Markdown report with headings and bullet points. \n"
        "If there are sources, include them at the end."
    ),
    "tools": [],
}

model = init_chat_model("openai:gpt-4.1-mini")



agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    subagents=[researcher_subagent, writer_subagent],
    system_prompt=(
        "You are a lead agent. \n"
        "Delegate research to researcher subagent, and then ask writer subagent to draft the report"
    ),
    backend=FilesystemBackend(root_dir=".", virtual_mode=True)
)

inputs = {
    "messages": [
        {"role": "user",
         "content": "Create and /notes.md with 10 bullet points on the topic of blackhole ?, call the internet_search tool to get the latest information "}
    ]
}

for update in agent.stream(inputs, stream_mode="updates"):
    print(update)

# results = agent.invoke({
#     "messages": [
#         {"role": "user",
#          "content": "Create and /notes.md with 10 bullet points on the topic of blackhole ?, call the internet_search tool to get the latest information "}
#     ]
# })
#
# print(results["messages"][-1].content)
