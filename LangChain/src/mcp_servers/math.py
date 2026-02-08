from fastmcp import FastMCP

mcp = FastMCP("Math")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiple two integers"""
    return a * b


if __name__ == "__main__":
    # STDIO transport is perfect for local servers
    # mcp.run(transport="stdio")
    mcp.run(transport="http", host="127.0.0.1", port=8000)
