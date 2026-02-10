import uuid
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()


@tool
def delete_file(path: str) -> str:
    """Delete a file Demo"""
    return f"Deleted {path}"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email Demo"""
    return f"Sent email to {to} with subject {subject}"


checkpointer = MemorySaver()

model = init_chat_model("openai:gpt-4.1-mini")

agent = create_deep_agent(
    model=model,
    tools=[delete_file, send_email],
    interrupt_on={
        "delete_file": True,
        "send_email": {"allowed_decisions": ["approve", "reject"]}
    },
    checkpointer=checkpointer,
    system_prompt="You are a helpful assistant, fulfil user requesting by using tools"
)

config = {"configurable": {"thread_id": str(uuid.uuid4())}}

result = agent.invoke({
    "messages": [
        {"role": "user",
         "content": "Delete temp.txt in root directory and email me the details to raj713335@gmail.com."}
    ]
},
    config=config
)

print(result["messages"][-1].content)

# If interrupted, approve deleting, reject email and then resume

if result.get("__interrupt__"):
    interrupt_payload = result["__interrupt__"][0].value
    actions = interrupt_payload["action_requests"]

    print("INTERRUPTED. Pending actions:")

    decisions = []

    for a in actions:
        if a["name"] == "delete_file":
            decisions.append({"type": "approve"})
        elif a["name"] == "send_email":
            decisions.append({"type": "reject"})

    result = agent.invoke(Command(resume={"decisions": decisions}), config=config)

print(result["messages"][-1].content)
