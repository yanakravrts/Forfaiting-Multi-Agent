from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from src.llm import get_llm_client
from src.prompts.orchestrator_prompt import orchestrator_prompt

_client = None
_agent = None


async def _get_agent():
    global _client, _agent
    if _agent is not None:
        return _agent

    _client = MultiServerMCPClient(
        {
            "forfaiting": {
                "transport": "sse",
                "url": "http://127.0.0.1:8080/sse",
            }
        }
    )
    tools = await _client.get_tools()
    llm = get_llm_client()
    _agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=orchestrator_prompt,
    )
    return _agent


async def ask_agent(user_message: str) -> str:
    agent = await _get_agent()
    result = await agent.ainvoke({"messages": [("user", user_message)]})
    return result["messages"][-1].content