import logging
import re
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from src.agents.factory import SPECIALIST_PROMPTS, get_specialist
from src.agents.tool_groups import Route
from src.graph.compare import run_discount_comparison, run_scheme_comparison
from src.graph.state import GraphState
from src.llm import get_llm_client
from src.prompts.clarify import clarify_prompt
from src.prompts.router import router_prompt

logger = logging.getLogger(__name__)

_graph = None


class RouteDecision(BaseModel):
    route: Literal[
        "discounting",
        "schema1",
        "schema2",
        "schema_compare",
        "discount_compare",
        "evaluation",
        "clarify",
    ] = Field(description="Best specialist route for the user request")
    reason: str = Field(description="Short reason for the routing choice")


_SCHEME_1 = re.compile(r"(схем[а-яіїє']*\s*1|scheme\s*1|schema\s*1)", re.IGNORECASE)
_SCHEME_2 = re.compile(r"(схем[а-яіїє']*\s*2|scheme\s*2|schema\s*2)", re.IGNORECASE)
_COMPARE = re.compile(
    r"(порівн|порівняльн|compare|comparison|обидв|обе\s+схем|side.by.side)",
    re.IGNORECASE,
)
_STRAIGHT = re.compile(
    r"(straight\s+discount|прям[аоийійє]?\s+дисконт|straight)",
    re.IGNORECASE,
)
_YIELD = re.compile(
    r"(discount\s+to\s+yield|yield\s+discount|дисконт\s+до\s+доход|до\s+yield|to\s+yield)",
    re.IGNORECASE,
)


def _needs_scheme_compare(text: str) -> bool:
    has_s1 = bool(_SCHEME_1.search(text))
    has_s2 = bool(_SCHEME_2.search(text))
    if has_s1 and has_s2:
        return True
    return bool(_COMPARE.search(text) and (has_s1 or has_s2))


def _needs_discount_compare(text: str) -> bool:
    has_straight = bool(_STRAIGHT.search(text))
    has_yield = bool(_YIELD.search(text))
    if has_straight and has_yield:
        return True
    if _COMPARE.search(text) and re.search(
        r"(дисконт|discount)", text, re.IGNORECASE
    ):
        return has_straight or has_yield
    return False


def _last_user_text(state: GraphState) -> str:
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return message.content
        if isinstance(message, tuple) and message[0] == "user":
            return message[1]
    return ""


def _keyword_route(text: str) -> str | None:
    if _needs_scheme_compare(text):
        return "schema_compare"
    if _needs_discount_compare(text):
        return "discount_compare"

    normalized = text.lower()

    if re.search(r"\b(npv|net present value|discount critical)\b", normalized):
        return "evaluation"
    if _SCHEME_2.search(text) and not _SCHEME_1.search(text):
        return "schema2"
    if _SCHEME_1.search(text) and not _SCHEME_2.search(text):
        return "schema1"
    if _STRAIGHT.search(text) or _YIELD.search(text):
        return "discounting"
    if re.search(r"\b(дисконт|discounting)\b", normalized):
        return "discounting"
    return None


async def classify_node(state: GraphState) -> dict:
    user_text = _last_user_text(state)
    keyword_route = _keyword_route(user_text)
    if keyword_route is not None:
        logger.info("[ROUTE] keyword -> %s", keyword_route)
        return {"route": keyword_route}

    llm = get_llm_client().with_structured_output(RouteDecision)
    decision: RouteDecision = await llm.ainvoke(
        [
            SystemMessage(content=router_prompt),
            HumanMessage(content=user_text),
        ]
    )
    logger.info("[ROUTE] llm -> %s (%s)", decision.route, decision.reason)
    return {"route": decision.route}


async def _run_specialist(route: Route, state: GraphState) -> dict:
    agent = await get_specialist(route)
    result = await agent.ainvoke({"messages": state["messages"]})
    new_messages = result["messages"][len(state["messages"]) :]
    if not new_messages:
        new_messages = [result["messages"][-1]]
    return {"messages": new_messages}


async def discounting_agent_node(state: GraphState) -> dict:
    return await _run_specialist("discounting", state)


async def schema1_agent_node(state: GraphState) -> dict:
    return await _run_specialist("schema1", state)


async def schema2_agent_node(state: GraphState) -> dict:
    return await _run_specialist("schema2", state)


async def compare_schemas_node(state: GraphState) -> dict:
    user_text = _last_user_text(state)
    content = await run_scheme_comparison(user_text)
    return {"messages": [AIMessage(content=content)]}


async def compare_discounts_node(state: GraphState) -> dict:
    user_text = _last_user_text(state)
    content = await run_discount_comparison(user_text)
    return {"messages": [AIMessage(content=content)]}


async def evaluation_agent_node(state: GraphState) -> dict:
    return await _run_specialist("evaluation", state)


async def clarify_node(state: GraphState) -> dict:
    llm = get_llm_client()
    response = await llm.ainvoke(
        [SystemMessage(content=clarify_prompt), *state["messages"]]
    )
    return {"messages": [response]}


def pick_route(state: GraphState) -> str:
    route = state.get("route") or "clarify"
    if route in ("schema_compare", "discount_compare"):
        return route
    if route not in SPECIALIST_PROMPTS:
        return "clarify"
    return route


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("classify", classify_node)
    graph.add_node("discounting_agent", discounting_agent_node)
    graph.add_node("schema1_agent", schema1_agent_node)
    graph.add_node("schema2_agent", schema2_agent_node)
    graph.add_node("compare_schemas", compare_schemas_node)
    graph.add_node("compare_discounts", compare_discounts_node)
    graph.add_node("evaluation_agent", evaluation_agent_node)
    graph.add_node("clarify", clarify_node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        pick_route,
        {
            "discounting": "discounting_agent",
            "schema1": "schema1_agent",
            "schema2": "schema2_agent",
            "schema_compare": "compare_schemas",
            "discount_compare": "compare_discounts",
            "evaluation": "evaluation_agent",
            "clarify": "clarify",
        },
    )
    graph.add_edge("discounting_agent", END)
    graph.add_edge("schema1_agent", END)
    graph.add_edge("schema2_agent", END)
    graph.add_edge("compare_schemas", END)
    graph.add_edge("compare_discounts", END)
    graph.add_edge("evaluation_agent", END)
    graph.add_edge("clarify", END)

    return graph.compile()


async def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
