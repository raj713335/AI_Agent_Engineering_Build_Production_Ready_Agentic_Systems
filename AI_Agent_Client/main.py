import os
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
import uvicorn

from utils.settings import initialize_settings
from routers import general_router


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan...")

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
    allow_headers=[""]
)


app.include_router(general_router.router)


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
