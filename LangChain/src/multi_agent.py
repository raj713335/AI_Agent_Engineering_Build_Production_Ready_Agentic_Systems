import os
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Callable, Any

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.agents.middleware import AgentState, before_model, after_model, wrap_model_call, ModelRequest, \
    ModelResponse, dynamic_prompt, PIIMiddleware, AgentMiddleware, hook_config, HumanInTheLoopMiddleware

from langgraph.runtime import Runtime
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

from tool import get_weather, calculate, search_docs, Context, get_user_id, send_email

load_dotenv()

model = init_chat_model("openai:gpt-4.1-mini")

# Sub - Agents developed my multiple teams

researcher_agent = create_agent(
    model=model,
    system_prompt="You are a research specialist..."
)

writer_agent = create_agent(
    model=model,
    system_prompt="You are a writing specialist..."
)

# Registry of available sub-agents
SUBAGENTS = {
    "researcher": researcher_agent,
    "writer": writer_agent
}


@tool
def task(agent_name: str, description: str) -> str:
    """Launch an ephemeral subagent for a task.

    Available agents:
    - researcher: Researcher and fact-finding
    -writer: Content creation and editing
    """

    agent = SUBAGENTS[agent_name]

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": description}
        ]
    })

    return result["messages"][-1].content


# Main coordinator agent
main_agent = create_agent(
    model=model,
    tools=[task],
    system_prompt=(
        "You coordinate specialised sub-agents."
        "Available: research (fact-finding),"
        "writer: (content creation."
        "Use the task tool to delegate work"
    )
)


result = main_agent.invoke({"messages": [
        {"role": "user", "content": "Can you write me a essay on black holes'"}
    ]})

print(result)

print("\n ---- FINAL ANSWER ----")
print(result["messages"][-1].content)




