import os
from dotenv import load_dotenv

from pydantic import BaseModel, Field

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from langgraph.checkpoint.memory import InMemorySaver

from tool import get_weather, calculate, search_docs, Context, get_user_id

load_dotenv()


class SupportActionPlan(BaseModel):
    """A structured plan for resolving a support request."""

    summary: str = Field(description="1-2 sentence summary of the issue")
    steps: list[str] = Field(description="Concrete steps the user should take")
    needs_human: bool = Field(description="True if a human should review before action")


def main():
    # Pick any model you have access to
    # These uses openAI with langchain-openai package

    model = init_chat_model("openai:gpt-4.1-mini")

    checkpointer = InMemorySaver()

    agent = create_agent(
        model=model,
        tools=[get_weather, calculate, search_docs, get_user_id],
        system_prompt="You are a helpful support assistant. Use tools when needed",
        checkpointer=checkpointer,
        response_format=SupportActionPlan
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

    config = {"configurable": {"thread_id": "demo-thread-1"}}

    for mode, chunk in agent.stream(
            {"messages": [{"role": "user", "content": "Search docs for API limits and summarize."}]},
            stream_mode=["updates", "messages"],
            config=config
    ):
        if mode == "messages":
            token, metadata = chunk
            if token.content:
                print(token.content, end="", flush=True)

        elif mode == "updates":
            # You can inspect node-level updates here
            pass

    print()


if __name__ == "__main__":
    main()
