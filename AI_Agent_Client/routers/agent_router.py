from fastapi import APIRouter, status
from typing import Any

import logging

from AI_Agent_Client.schemas.AgentQueryRequest import AgentQueryRequest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/api/agent", tags=["Agent API"])

_agent = None


def configure_agent_router(agent):
    global _agent
    _agent = agent


@router.post("/query")
async def agentic_query(request: AgentQueryRequest) -> Any:
    logger.info("Received HTTP POST /api/agent/query request")

    if _agent is None:
        return {"error": "Agent not initialized"}

    result = await _agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": request.query
            }
        ]
    })

    for msg in result["messages"]:
        if msg.type == "tool":
            logger.info(f"Tool Called: {msg.name}")
            logger.info(f"Tool Input: {msg.content}")

    return {"message": result["messages"][-1].content}
