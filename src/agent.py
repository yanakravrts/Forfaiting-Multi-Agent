from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from src.agents.factory import get_specialist
from src.graph.supervisor import get_graph

ChatTurn = dict[str, str]


def history_to_messages(history: list[ChatTurn]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for turn in history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        elif turn["role"] == "assistant":
            messages.append(AIMessage(content=turn["content"]))
    return messages


async def ask_agent(user_message: str, history: list[ChatTurn] | None = None) -> str:
    graph = await get_graph()
    messages = history_to_messages(history or [])
    messages.append(HumanMessage(content=user_message))
    result = await graph.ainvoke({"messages": messages})
    return result["messages"][-1].content


async def ask_orchestrate(user_message: str) -> str:
    """Discounting-only path (manager shortcut for straight / yield requests)."""
    agent = await get_specialist("discounting")
    result = await agent.ainvoke({"messages": [HumanMessage(content=user_message)]})
    return result["messages"][-1].content
