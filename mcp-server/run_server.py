#!/usr/bin/env python3
"""Run the cookbook recipe MCP server over stdio."""

from server import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
