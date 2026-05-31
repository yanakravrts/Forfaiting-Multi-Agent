import asyncio
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.factory import get_specialist
from src.agents.tool_groups import Route
from src.llm import get_llm_client
from src.prompts.compare import (
    DISCOUNT_SYNTHESIZER_PROMPT,
    SCHEME1_SUBTASK,
    SCHEME2_SUBTASK,
    SCHEME_SYNTHESIZER_PROMPT,
    STRAIGHT_DISCOUNT_SUBTASK,
    YIELD_DISCOUNT_SUBTASK,
)

logger = logging.getLogger(__name__)


async def _run_subtask(route: Route, subtask_prompt: str, user_text: str) -> str:
    agent = await get_specialist(route)
    message = HumanMessage(
        content=f"{subtask_prompt.strip()}\n\n---\nUser request:\n{user_text}"
    )
    result = await agent.ainvoke({"messages": [message]})
    text = result["messages"][-1].content
    logger.info("[COMPARE] subtask %s done (%d chars)", route, len(text))
    return text


async def _synthesize(
    system_prompt: str,
    user_text: str,
    sections: dict[str, str],
    title: str,
) -> str:
    blocks = "\n\n".join(
        f"### {label}\n\n{body}" for label, body in sections.items()
    )
    llm = get_llm_client()
    response = await llm.ainvoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=(
                    f"# {title}\n\n"
                    f"**User request:**\n{user_text}\n\n"
                    f"**Calculation results from workers:**\n\n{blocks}"
                )
            ),
        ]
    )
    return response.content


async def run_scheme_comparison(user_text: str) -> str:
    scheme1_result, scheme2_result = await asyncio.gather(
        _run_subtask("schema1", SCHEME1_SUBTASK, user_text),
        _run_subtask("schema2", SCHEME2_SUBTASK, user_text),
    )

    return await _synthesize(
        SCHEME_SYNTHESIZER_PROMPT,
        user_text,
        {
            "Схема 1 (Scheme 1)": scheme1_result,
            "Схема 2 (Scheme 2)": scheme2_result,
        },
        "Порівняльний розрахунок: Схема 1 та Схема 2",
    )


async def run_discount_comparison(user_text: str) -> str:
    straight_result, yield_result = await asyncio.gather(
        _run_subtask("discounting", STRAIGHT_DISCOUNT_SUBTASK, user_text),
        _run_subtask("discounting", YIELD_DISCOUNT_SUBTASK, user_text),
    )

    return await _synthesize(
        DISCOUNT_SYNTHESIZER_PROMPT,
        user_text,
        {
            "Straight discounting": straight_result,
            "Discount to yield": yield_result,
        },
        "Порівняння методів дисконтування",
    )
