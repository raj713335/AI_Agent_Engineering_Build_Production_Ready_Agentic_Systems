import modal
from langchain.chat_models import init_chat_model

from deepagents import create_deep_agent
from langchain_modal import ModalSandbox


from dotenv import load_dotenv

load_dotenv()

model = init_chat_model("openai:gpt-4.1-mini")

app = modal.App.lookup("your-app")
modal_sandbox = modal.Sandbox.create(app=app)
backend = ModalSandbox(sandbox=modal_sandbox)

agent = create_deep_agent(
    model=model,
    system_prompt="You are a Python coding assistant with sandbox access.",
    backend=backend
)

results = agent.invoke({
    "messages": [
        {"role": "user",
         "content": "create a small python package and run pytest"}
    ]
})

modal_sandbox.terminate()