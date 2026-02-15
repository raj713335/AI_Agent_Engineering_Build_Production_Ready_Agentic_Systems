from fastapi import APIRouter, status, Request, HTTPException
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from typing import Any

import logging

from AI_Agent_MCP_Server.tookit.tools import tools

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/api", tags=["General"])


@router.get("/healthcheck", status_code=status.HTTP_200_OK)
def perform_healthcheck() -> Any:
    """Returns a 200 when API is running."""
    logger.info("Healthcheck performed")
    return {"message": "AI Agent Client is Running..."}


@router.get("/tools", status_code=status.HTTP_200_OK)
async def list_mcp_tools():
    logger.info("Listing all the available MCP tools")
    try:
        result: list[dict[str, str]] = []
        for tool in tools:
            name = getattr(tool, "name", None)
            description = getattr(tool, "description", None)

            result.append((
                {
                    "name": str(name) if name is not None else str(tool),
                    "description": str(description) if description is not None else "",
                }
            ))

            return result
    except HTTPException:
        raise
    except Exception as ex:
        logger.exception(f"Failed to list MCP tools: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list MCP tools"
        ) from ex


@router.get("/docs", include_in_schema=False)
async def swagger_ui_html() -> Any:
    """Swagger UI HTML"""
    return swagger_ui_html(
        openapi=router.openapi_url,
        title="MCP Server Docs",
        swagger_ui_parameters={"syntaxHighlight.theme": "nord"},
        swagger_css_url="/resources/swagger-ui.css"
    )
