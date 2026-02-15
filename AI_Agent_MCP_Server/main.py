import os
import logging
import asyncio

from contextlib import asynccontextmanager, AsyncExitStack

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from langchain_mcp_adapters.tools import to_fastmcp

from dotenv import load_dotenv
import uvicorn

from utils.settings import initialize_settings
from AI_Agent_MCP_Server.tookit.tools import tools
from AI_Agent_MCP_Server.routers import general_router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

# Create a MCP Server
mcp_server = FastMCP(
    name=os.getenv("MCP_APP_NAME", "AI_AGENT_MCP"),
    instructions="A MCP Server exposing tools for Researcher Agent",
    tools=[to_fastmcp(tool) for tool in tools],
    streamable_http_path="/mcp",
    json_response=True,
    stateless_http=False,
    host="0.0.0.0"
)

http_app = mcp_server.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MCP application lifespan...")

    async with AsyncExitStack() as stack:
        await stack.enter_async_context(http_app.router.lifespan_context(http_app))
        logger.info("Starting MCP Server...")
        asyncio.create_task(mcp_server.run_stdio_async())
        yield



app = FastAPI(
    title="AI Agent MCP Server",
    description="MCP Server for AI Agent Client",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[""]
)

app.include_router(general_router.router)
app.mount("/api", http_app, name="mcp-http") # adding mcp mount to default fastapi server




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
