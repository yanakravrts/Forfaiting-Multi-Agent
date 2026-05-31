from typing import Annotated, Literal

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from src.agents.tool_groups import Route

GraphRoute = Route | Literal["schema_compare", "discount_compare"]


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    route: GraphRoute | None
