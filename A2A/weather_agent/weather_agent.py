"""
Weather Agent — Google ADK LlmAgent that uses MCP tools via stdio.

The agent connects to weather_mcp.py (Server B) as an MCP client,
gets weather tools, and uses OpenAI (via LiteLLM) as the LLM.
"""

import os
import sys

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp.client.stdio import StdioServerParameters


def create_weather_agent() -> LlmAgent:
    """Create a weather agent that gets tools from the MCP server (stdio)."""
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # MCP Client B → Server B (weather_mcp.py via stdio)
    mcp_server_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "weather_mcp.py"
    )
    weather_toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[mcp_server_script],
            ),
        ),
    )

    return LlmAgent(
        model=LiteLlm(model=model_name),
        name="weather_agent",
        description="An agent that answers weather questions using dummy data",
        instruction=(
            "You are a friendly weather assistant. "
            "Use the get_weather tool to look up current weather, "
            "and the get_forecast tool for multi-day forecasts. "
            "Always call the tool first — never make up weather data. "
            "Format your response nicely in Markdown."
        ),
        tools=[weather_toolset],
    )