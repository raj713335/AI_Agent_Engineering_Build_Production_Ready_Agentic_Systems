"""
Weather Agent Server — FastAPI + A2A protocol.

Architecture: A2A Server ← Weather Agent ← MCP Client B → MCP Server B (stdio)

Endpoints:
    POST /ask       → Simple REST (ask the agent a question)
    GET  /health    → Health check
    POST /a2a       → A2A JSON-RPC (multi-agent communication)
    GET  /.well-known/agent-card.json → A2A agent discovery
"""

import logging
import os
import sys
import uuid

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# A2A SDK
from a2a.server.request_handlers import DefaultRequestHandlerV2
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils import TransportProtocol

# Google ADK Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Local
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from weather_agent.weather_agent import create_weather_agent  # noqa: E402
from weather_agent.weather_executor import WeatherExecutor    # noqa: E402

load_dotenv()
logging.basicConfig(level=logging.INFO)

HOST = "0.0.0.0"
PORT = 10001


# ── Request / Response models ─────────────────────────────────────────────

class AskRequest(BaseModel):
    query: str = Field(..., example="What is the weather in New York?")
    session_id: str | None = Field(default=None)

class AskResponse(BaseModel):
    answer: str
    session_id: str


# ── Agent Card ────────────────────────────────────────────────────────────

def build_agent_card() -> AgentCard:
    skill = AgentSkill()
    skill.id = "weather_search"
    skill.name = "Search weather"
    skill.description = "Answers weather questions for any city"
    skill.tags.extend(["weather"])
    skill.examples.extend(["What is the weather in Tokyo?"])

    caps = AgentCapabilities()
    caps.streaming = True

    iface = AgentInterface()
    iface.url = os.environ.get("APP_URL", f"http://{HOST}:{PORT}")
    iface.protocol_binding = TransportProtocol.JSONRPC.value

    card = AgentCard()
    card.name = "Weather Agent"
    card.description = "A weather agent that returns dummy weather data"
    card.version = "1.0.0"
    card.default_input_modes.extend(["text"])
    card.default_output_modes.extend(["text"])
    card.capabilities.CopyFrom(caps)
    card.skills.append(skill)
    card.supported_interfaces.append(iface)
    return card


# ── FastAPI Application ───────────────────────────────────────────────────

def create_app() -> FastAPI:
    agent_card = build_agent_card()
    agent = create_weather_agent()
    runner = Runner(
        app_name=agent_card.name,
        agent=agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )

    app = FastAPI(
        title="🌤️ Weather Agent API",
        version="1.0.0",
        description="AI weather agent with dummy data. POST to `/ask` to try it.",
    )

    @app.post("/ask", response_model=AskResponse, tags=["Weather"])
    async def ask(body: AskRequest) -> AskResponse:
        session_id = body.session_id or uuid.uuid4().hex
        session = await runner.session_service.get_session(
            app_name=runner.app_name, user_id="user", session_id=session_id
        )
        if session is None:
            session = await runner.session_service.create_session(
                app_name=runner.app_name, user_id="user", session_id=session_id
            )

        final_text = ""
        try:
            async for event in runner.run_async(
                session_id=session.id,
                user_id="user",
                new_message=genai_types.UserContent(
                    parts=[genai_types.Part(text=body.query)]
                ),
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_text = "\n".join(
                            p.text for p in event.content.parts if p.text
                        )
                    break
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

        return AskResponse(answer=final_text or "(no response)", session_id=session.id)

    @app.get("/health", tags=["System"])
    async def health():
        return {"status": "ok"}

    # ── A2A routes ────────────────────────────────────────────────────
    handler = DefaultRequestHandlerV2(
        agent_executor=WeatherExecutor(runner, agent_card),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )
    for route in create_jsonrpc_routes(handler, rpc_url="/a2a", enable_v0_3_compat=True):
        app.routes.append(route)
    for route in create_agent_card_routes(agent_card=agent_card):
        app.routes.append(route)

    return app


# ── Entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("ERROR: Set OPENAI_API_KEY first.")

    print(f"🌤️  Weather Agent on http://localhost:{PORT}")
    print(f"📖  Docs at http://localhost:{PORT}/docs")
    app = create_app()
    uvicorn.run(app, host=HOST, port=PORT)