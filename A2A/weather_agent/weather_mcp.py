"""
Dummy Weather MCP Server (Server B in the architecture diagram).

Exposes weather tools via stdio MCP transport.
Uses fake/random data — no real API calls.

Run standalone:  python -m weather_agent.weather_mcp
"""

import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")


@mcp.tool()
async def get_weather(city: str) -> dict:
    """Get the current weather for a city.

    Args:
        city: Name of the city (e.g. "New York", "London", "Tokyo")
    """
    temp_f = random.randint(15, 95)
    return {
        "city": city,
        "temperature_f": temp_f,
        "temperature_c": round((temp_f - 32) * 5 / 9, 1),
        "condition": random.choice(
            ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy", "Partly Cloudy"]
        ),
        "humidity_percent": random.randint(20, 90),
        "wind_mph": random.randint(0, 30),
    }


@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> dict:
    """Get a multi-day weather forecast for a city.

    Args:
        city: Name of the city
        days: Number of days to forecast (1-7)
    """
    days = min(max(days, 1), 7)
    forecast = []
    for day in range(1, days + 1):
        forecast.append({
            "day": day,
            "high_f": random.randint(50, 95),
            "low_f": random.randint(20, 60),
            "condition": random.choice(
                ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy"]
            ),
        })
    return {"city": city, "forecast": forecast}


if __name__ == "__main__":
    mcp.run(transport="stdio")