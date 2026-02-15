import os
import logging

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient

from dotenv import load_dotenv
import uvicorn

from utils.settings import initialize_settings
from routers import general_router, agent_router
from utils import prompt
# from database.database_connection import engine
# from models.chat_history import Base


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

client: Optional[MultiServerMCPClient] = None
agent_instance = None


def get_mcp_client() -> MultiServerMCPClient:
    mcp_server_name = os.getenv("MCP_APP_NAME")
    mcp_server_url = os.getenv("MCP_APP_URL")
    mcp_server_transport = os.getenv("MCP_SERVER_TRANSPORT")

    return MultiServerMCPClient({
        mcp_server_name: {
            "url": mcp_server_url,
            "transport": mcp_server_transport,
            "timeout": 600
        }
    })


async def setup_agent_client():
    global client

    if client is None:
        client = get_mcp_client()

    model = init_chat_model("openai:gpt-4.1-mini")

    tools = await client.get_tools()

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=prompt.PROMPT
    )

    return agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_instance
    logger.info("Starting application lifespan...")

    # async with engine.begin() as conn:
    #     await conn.run_async(Base.metadata.create_all)

    agent_instance = await setup_agent_client()

    agent_router.configure_agent_router(agent_instance)

    yield

    logger.info("Application lifespan ended.")

app = FastAPI(
    title="AI Agent Client API",
    description="API for AI Agent Client",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(general_router.router)
app.include_router(agent_router.router)


# Initialize settings
logger.info("Initialize application settings")
app_settings = initialize_settings()

if __name__ == "__main__":
    logger.info("Starting Uvicorn")
    uvicorn.run(
        app="main:app",
        host=app_settings.app_host,
        port=app_settings.app_port,
        reload=app_settings.app_reload,
        workers=app_settings.workers
    )