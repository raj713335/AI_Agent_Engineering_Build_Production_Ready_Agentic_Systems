from fastapi import APIRouter, status
from typing import Any

import logging

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from AI_Agent_Client.utils import prompt
from AI_Agent_Client.schemas.AgentQueryRequest import AgentQueryRequest

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

router = APIRouter(prefix="/api/agent", tags=["Agent API"])

model = init_chat_model("openai:gpt-4.1-mini")

agent = create_agent(
    model=model,
    system_prompt=prompt.PROMPT
)


@router.post("/query")
def agentic_query(request: AgentQueryRequest) -> Any:
    """Returns a Agentic Query Response"""
    logger.info("Received HTTP POST /api/agent/query request")

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": request.query
            }
        ]
    })

    return {"message": result["messages"][-1].content}
