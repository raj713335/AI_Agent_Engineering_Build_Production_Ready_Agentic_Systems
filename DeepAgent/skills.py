import uuid
from urllib.request import urlopen
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

checkpointer = InMemorySaver()

skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagentsjs/refs/heads/main/examples/skills/langgraph-docs/SKILL.md"

with urlopen(skill_url) as response:
    print(response)
    skill_content = response.read().decode("utf-8")

skills_files = {
    "/skills/langgraph-docs/skills.md": skill_content
}

model = init_chat_model("openai:gpt-4.1-mini")


agent = create_deep_agent(
    model=model,
    skills=["./skills"],
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": str(uuid.uuid4())}}

result = agent.invoke({
    "messages": [
        {"role": "user",
         "content": "What is langgraph"}
    ],
    "files": skills_files
},
    config=config
)

print(result["messages"][-1].content)