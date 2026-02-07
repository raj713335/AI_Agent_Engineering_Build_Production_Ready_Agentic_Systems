import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from langgraph.checkpoint.memory import InMemorySaver

from tool import get_weather, calculate, search_docs, Context, get_user_id

load_dotenv()


def main():
    # Pick any model you have access to
    # These uses openAI with langchain-openai package

    model = init_chat_model("openai:gpt-4.1-mini")

    checkpointer = InMemorySaver()

    agent = create_agent(
        model=model,
        tools=[get_weather, calculate, search_docs, get_user_id],
        system_prompt="You are a helpful assistant. Use tools when needed",
        checkpointer=checkpointer
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

    config = {"configurable": {"thread_id": "demo-thread-1"}}

    result = agent.invoke({"messages": [
        {"role": "user", "content": "what is my user id?"}
    ]},
        context=Context(user_id="raj713335"),
        config=config,
    )

    print("\n ---- FINAL ANSWER ----")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
