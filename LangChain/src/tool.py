from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""

    # Replace with real API later
    return f"It's always sunny in {city}"


@tool
def calculate(expression: str) -> str:
    """Evaluate a simple math expression like '12 * (3 + 5)' """

    return str(eval(expression))
