from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.agents.tool_groups import TOOL_GROUPS, Route
from src.llm import get_llm_client
from src.prompts.clarify import clarify_prompt
from src.prompts.discounting import discounting_prompt
from src.prompts.evaluation import evaluation_prompt
from src.prompts.schema1 import schema1_prompt
from src.prompts.schema2 import schema2_prompt

MCP_SERVER_URL = "http://127.0.0.1:8080/sse"

SPECIALIST_PROMPTS: dict[str, str] = {
    "discounting": discounting_prompt,
    "schema1": schema1_prompt,
    "schema2": schema2_prompt,
    "evaluation": evaluation_prompt,
    "clarify": clarify_prompt,
}

_client: MultiServerMCPClient | None = None
_all_tools: list | None = None
_specialists: dict[str, object] = {}


async def get_mcp_tools() -> list:
    global _client, _all_tools
    if _all_tools is not None:
        return _all_tools

    _client = MultiServerMCPClient(
        {
            "forfaiting": {
                "transport": "sse",
                "url": MCP_SERVER_URL,
            }
        }
    )
    _all_tools = await _client.get_tools()
    return _all_tools


def filter_tools(all_tools: list, names: set[str]) -> list:
    return [tool for tool in all_tools if getattr(tool, "name", None) in names]


async def get_specialist(route: Route):
    if route == "clarify":
        raise ValueError("clarify route has no tool specialist")

    if route in _specialists:
        return _specialists[route]

    all_tools = await get_mcp_tools()
    tool_names = TOOL_GROUPS[route]
    tools = filter_tools(all_tools, tool_names)
    llm = get_llm_client()
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SPECIALIST_PROMPTS[route],
        name=f"{route}_agent",
    )
    _specialists[route] = agent
    return agent
