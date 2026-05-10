import os
import logging
import uvicorn
from datetime import datetime
from mcp.server.fastmcp import FastMCP

from src.tools import register_discounting_tools, register_schema1_tools


# Configure logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = f"{LOG_DIR}/server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)


# Create MCP server
mcp = FastMCP("Forfaiting-Multi-Agent Server")
register_discounting_tools(mcp)
register_schema1_tools(mcp)

app = mcp.sse_app()


if __name__ == "__main__":
    logging.info("Starting server")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8080,
        timeout_keep_alive=300,
    )

    logging.info("Server stopped")