import asyncio
from pathlib import Path

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from dotenv import load_dotenv

# PROJECT_ROOT = Path(__file__).resolve().parents[1]
# MATH_SERVER = PROJECT_ROOT / "src" / "mcp_servers" / "math.py"
#
# print(MATH_SERVER)

load_dotenv()


async def main():
    # MultiServerMCPClient can mix transports
    # - stdio: spawn a local process
    # - http: connect to a running server by URL

    client = MultiServerMCPClient(
        {
            # "math": {
            #     "command": "python",
            #     "args": [str(MATH_SERVER)],
            #     "transport": "stdio"
            # },
            "math": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "http"
            }
        }
    )

    tools = await client.get_tools()

    model = init_chat_model("openai:gpt-4.1-mini")

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You are a helpful assistant. Use tools when needed."
            "If math is required, call the math tools."
        ),
    )

    r1 = await agent.ainvoke({"messages": "What is (3+5) x 12?"})

    print("\n --- RESULT ---")
    print(r1["messages"][-1].content)


async def run_stateful():
    # MultiServerMCPClient can mix transports
    # - stdio: spawn a local process
    # - http: connect to a running server by URL

    client = MultiServerMCPClient(
        {
            # "math": {
            #     "command": "python",
            #     "args": [str(MATH_SERVER)],
            #     "transport": "stdio"
            # },
            "math": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "http"
            }
        }
    )

    async with client.session("math") as session:
        tools = await load_mcp_tools(session)

        model = init_chat_model("openai:gpt-4.1-mini")

        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=(
                "You are a helpful assistant. Use tools when needed."
                "If math is required, call the math tools."
            ),
        )

        r1 = await agent.ainvoke({"messages": "What is (3+5) x 12?"})

        print("\n --- RESULT ---")
        print(r1["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(run_stateful())
