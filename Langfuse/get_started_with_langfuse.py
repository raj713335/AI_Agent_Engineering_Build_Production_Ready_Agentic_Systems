from dotenv import load_dotenv

from langfuse import get_client
from langfuse.langchain import CallbackHandler

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

load_dotenv()

# Initialize Langfuse Client
langfuse = get_client()

# Initialize Langfuse CallbackHandler for Langchain (tracing)

langfuse_handler = CallbackHandler()


def add_numbers(a: int, b: int) -> int:
    """Add two numbers together and return the result."""
    return a + b


model = init_chat_model("openai:gpt-4.1-mini")

agent = create_agent(
    model=model,
    tools=[add_numbers],
    system_prompt="You are a helpful assistance, who can do calculations based on tools provided "
)

result = agent.invoke(
    {"messages":
     [{"role": "user",
       "content": "what is 47 + 23 ?"}]
     },
    config={"callbacks": [langfuse_handler]}
)

print(result["messages"][-1].content)
