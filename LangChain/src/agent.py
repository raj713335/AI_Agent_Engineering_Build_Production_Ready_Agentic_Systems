import os
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from typing import Callable

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.agents.middleware import AgentState, before_model, after_model, wrap_model_call, ModelRequest, \
    ModelResponse, dynamic_prompt
from langgraph.runtime import Runtime

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

from tool import get_weather, calculate, search_docs, Context, get_user_id

load_dotenv()


@dataclass
class Context:
    user_id: str


store = InMemoryStore()


@tool
def save_preference(style: str, runtime: ToolRuntime[Context]) -> str:
    """Save the user's preference response style."""
    store = runtime.store
    store.put(("preferences",), runtime.context.user_id, {"style": style})
    return "Saved."


@tool
def read_preference(runtime: ToolRuntime[Context]) -> str:
    """Read the user's preference style."""
    pref = runtime.store.get(("preferences",), runtime.context.user_id)
    return pref.value.get("style", "balanced") if pref else "balance"


class SupportActionPlan(BaseModel):
    """A structured plan for resolving a support request."""

    summary: str = Field(description="1-2 sentence summary of the issue")
    steps: list[str] = Field(description="Concrete steps the user should take")
    needs_human: bool = Field(description="True if a human should review before action")


@before_model
def log_before_model(state: AgentState, runtime: Runtime):
    last = state["messages"][-1]
    print(f"[before_model] last message: {getattr(last, 'content', last)}")
    return None


@after_model
def log_after_model(state: AgentState, runtime: Runtime):
    last = state["messages"][-1]
    print(f"[after_model] model output: {getattr(last, 'content', last)}")
    return None


@wrap_model_call
def retry_model(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    for attempt in range(3):
        try:
            return handler(request)
        except Exception as ex:
            if attempt == 2:
                print(f"[wrap_model_call] retry {attempt + 1}/3 after error: {ex}")
                raise
            print(f"[wrap_model_call] retry {attempt + 1}/3 after error: {ex}")


@dynamic_prompt
def system_prompt_from_context(request: ModelRequest) -> str:
    # Example: be extra concise for long conversation
    if len(request.messages) > 10:
        return "You are a helpful assistant. Be extremely concise."
    return "You are a helpful assistant."


def main():
    # Pick any model you have access to
    # These uses openAI with langchain-openai package

    model = init_chat_model("openai:gpt-4.1-mini")

    checkpointer = InMemorySaver()

    agent = create_agent(
        model=model,
        tools=[get_weather, calculate, search_docs, get_user_id, save_preference, read_preference],
        system_prompt="You are a helpful support assistant. Use tools when needed",
        #checkpointer=checkpointer,
        #response_format=SupportActionPlan,
        store=store,
        # middleware=[
        #     SummarizationMiddleware(
        #         model="openai:gpt-4.1-mini",
        #         trigger=("tokens", 4000),
        #         keep=("messages", 20)
        #     )
        #]
        middleware=[
            log_after_model,
            log_before_model,
            system_prompt_from_context,
            retry_model
        ]
    )

    # config = {"configurable": {"thread_id": "demo-thread-1"}}
    #
    # result = agent.invoke({"messages": [
    #     {"role": "user", "content": "what is the weather in Delhi? and what's (3+5)*12?"}
    # ]},
    #     config=config,
    # )

    # print("\n --- FULL MESSAGE TRACE ---")
    # for m in result["messages"]:
    #     print(type(m), getattr(m, "content", None))

    # print("\n ---- FINAL ANSWER 1----")
    # print(result["messages"][-1].content)
    #
    # result = agent.invoke({"messages": [
    #     {"role": "user", "content": "what city did I say I want to get the weather of ?"}
    # ]},
    #     config=config,
    # )
    #
    # print("\n ---- FINAL ANSWER 2----")
    # print(result["messages"][-1].content)

    # config = {"configurable": {"thread_id": "demo-thread-1"}}
    #
    # result = agent.invoke({"messages": [
    #     {"role": "user", "content": "I can't reset my password. What do I do ?"}
    # ]},
    #     context=Context(user_id="raj713335"),
    #     config=config,
    # )
    #
    # print("\n ---- FINAL ANSWER ----")
    # print(result["structured_response"])
    # print(result["messages"][-1].content)

    #config = {"configurable": {"thread_id": "demo-thread-1"}}

    # for mode, chunk in agent.stream(
    #         {"messages": [{"role": "user", "content": "Search docs for API limits and summarize."}]},
    #         stream_mode=["updates", "messages"],
    #         config=config
    # ):
    #     if mode == "messages":
    #         token, metadata = chunk
    #         if token.content:
    #             print(token.content, end="", flush=True)
    #
    #     elif mode == "updates":
    #         # You can inspect node-level updates here
    #         pass
    #
    # print()

    #config = {"configurable": {"thread_id": "demo-thread-1"}}

    agent.invoke({"messages": [
        {"role": "user", "content": "My Style is: super concise."}
    ]},
        context=Context(user_id="raj713335"),
    )

    result = agent.invoke({"messages": [
        {"role": "user",
         "content": "can you calculate 7*5*5, can you find me the best hotel in my area with 500 budget"}
    ]},
        context=Context(user_id="raj713335"),
    )

    print("\n ---- FINAL ANSWER ----")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
