from fastapi import APIRouter, status
from typing import Any

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/api", tags=["General"])


@router.get("/healthcheck", status_code=status.HTTP_200_OK)
def perform_healthcheck() -> Any:
    """Returns a 200 when API is running."""
    logger.info("Healthcheck performed")
    return {"message": "AI Agent Client is Running..."}
