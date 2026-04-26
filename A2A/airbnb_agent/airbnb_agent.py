"""
Airbnb Agent — Google ADK LlmAgent that uses MCP tools via stdio.

The agent connects to airbnb_mcp.py (Server A) as an MCP client,
gets Airbnb search tools, and uses OpenAI (via LiteLLM) as the LLM.
"""

import os
import sys

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp.client.stdio import StdioServerParameters

SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]


def create_airbnb_agent() -> LlmAgent:
    """Create an Airbnb agent that gets tools from the MCP server (stdio)."""
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # MCP Client A → Server A (airbnb_mcp.py via stdio)
    mcp_server_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "airbnb_mcp.py"
    )
    airbnb_toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[mcp_server_script],
            ),
        ),
    )

    return LlmAgent(
        model=LiteLlm(model=model_name),
        name="airbnb_agent",
        description="An agent that helps search Airbnb accommodation",
        instruction=(
            "You are a specialized assistant for Airbnb accommodations. "
            "Use the search_listings tool to find listings and "
            "get_listing_details for more info on a specific listing. "
            "Always call the tool first — never invent listings or prices. "
            "Format your response nicely in Markdown with links to listings."
        ),
        tools=[airbnb_toolset],
    )