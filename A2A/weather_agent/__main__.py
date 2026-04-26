import logging
import os

import click
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from weather_executor import WeatherExecutor
from weather_agent import create_weather_agent


load_dotenv()
logging.basicConfig()

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 10001


def create_app():

    # Skill
    skill = AgentSkill(
        id="weather_search",
        name="Search weather",
        description="Helps with weather in city or states",
        tags=["weather"],
        examples=["weather in LA, CA"],
    )

    app_url = os.environ.get("APP_URL", f"http://{DEFAULT_HOST}:{DEFAULT_PORT}")

    # Agent Card
    agent_card = AgentCard(
        name="Weather Agent",
        description="Helps with weather",
        url=app_url,
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    # ADK Runner
    adk_agent = create_weather_agent()
    runner = Runner(
        app_name=agent_card.name,
        agent=adk_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )

    agent_executor = WeatherExecutor(runner, agent_card)

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Weather Agent running"}

    @app.post("/")
    async def handle_request(request: Request):
        body = await request.json()
        response = await request_handler.handle(body)
        return JSONResponse(content=response)

    return app


@click.command()
@click.option("--host", default=DEFAULT_HOST)
@click.option("--port", default=DEFAULT_PORT)
def cli(host, port):
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
