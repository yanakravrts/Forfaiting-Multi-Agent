import asyncio
import os

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("FORFAITING_API_URL", "http://127.0.0.1:8000").rstrip("/")
CHAT_ENDPOINT = "chat"
MAX_CHAT_HISTORY = 10

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Асистент з форфейтингу",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# STYLES
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

/* ── RESET & BACKGROUND ─────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section,
.stApp, .main,
[data-testid="stMainBlockContainer"] {
    background: transparent !important;
}

.stApp {
    background:
        radial-gradient(ellipse 80% 60% at 15% 0%,   #fff9c2 0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 85% 10%,  #bfdbfe 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 50% 100%, #e0f2fe 0%, transparent 60%),
        #f8fafc !important;
    font-family: "Inter", sans-serif !important;
    color: #0f2a45 !important;
}

[data-testid="stHeader"]  { background: transparent !important; }
#MainMenu { visibility: hidden !important; }
footer    { visibility: hidden !important; }

/* ── SIDEBAR ─────────────────────────────────────────────── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background: rgba(255,255,255,0.92) !important;
    backdrop-filter: blur(12px) !important;
    border-right: 1px solid rgba(147,197,253,0.4) !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] {
    z-index: 300 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #0f3460 !important; }

section[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #3b82f6, #1e40af) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* ── ЦЕНТРАЛЬНИЙ КОНТЕЙНЕР (welcome screen) ─────────────── */
.welcome-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 72vh;
    padding: 0 24px;
    text-align: center;
}

.welcome-icon {
    font-size: 52px;
    margin-bottom: 16px;
    filter: drop-shadow(0 4px 16px rgba(59,130,246,0.18));
}

.welcome-title {
    font-family: "Playfair Display", serif;
    font-size: 46px;
    font-weight: 700;
    color: #0f3460;
    line-height: 1.15;
    margin-bottom: 10px;
    letter-spacing: -0.02em;
}

.welcome-sub {
    font-size: 17px;
    color: #4a7090;
    margin-bottom: 36px;
    font-weight: 400;
}

/* ── CHAT INPUT (bottom dock + field) ───────────────────── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div,
[data-testid="stBottomBlockContainer"] section {
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
}

.stChatInputContainer,
[data-testid="stChatInput"],
[class*="chatInput"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1.5px solid rgba(147,197,253,0.8) !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 24px rgba(59,130,246,0.12) !important;
    color-scheme: light !important;
}

/* усі вкладені обгортки Base UI / Emotion */
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="textarea"] > div,
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="base-input"] > div {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border-color: transparent !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea,
.stChatInputContainer textarea,
textarea[data-testid="stChatInputTextArea"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #0f2a45 !important;
    caret-color: #3b82f6 !important;
    font-family: "Inter", sans-serif !important;
    font-size: 15px !important;
    -webkit-text-fill-color: #0f2a45 !important;
}

textarea[data-testid="stChatInputTextArea"]::placeholder {
    color: #94b8d4 !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] button,
.stChatInputContainer button {
    background: linear-gradient(135deg, #f5c842, #3b82f6) !important;
    background-color: transparent !important;
    border-radius: 12px !important;
    border: none !important;
}

/* ── CHAT MESSAGES ───────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 2px 0 !important;
    margin-bottom: 4px !important;
    animation: fadeIn 0.22s ease;
}

[data-testid="stChatMessage"] > div:last-child {
    border-radius: 18px !important;
    padding: 13px 18px !important;
    border: 1px solid transparent !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child {
    background: linear-gradient(135deg, #fffaeb, #fef3c7) !important;
    border-color: #fde68a !important;
    box-shadow: 0 2px 12px rgba(245,200,66,0.15) !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:last-child {
    background: rgba(255,255,255,0.92) !important;
    border-color: #bfdbfe !important;
    box-shadow: 0 2px 12px rgba(59,130,246,0.10) !important;
    backdrop-filter: blur(8px) !important;
}

/* TEXT */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] td,
[data-testid="stChatMessage"] th,
[data-testid="stChatMessage"] span,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] td,
[data-testid="stMarkdownContainer"] th {
    color: #0f2a45 !important;
    font-size: 15px !important;
    line-height: 1.75 !important;
}
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 { color: #0f3460 !important; }
[data-testid="stChatMessage"] strong { color: #0f3460 !important; }
[data-testid="stChatMessage"] code {
    background: #eff6ff !important;
    color: #1e40af !important;
    border-radius: 5px !important;
}

/* TABLES */
[data-testid="stChatMessage"] table {
    background: white !important;
    border-radius: 12px !important;
    border: 1px solid #bfdbfe !important;
    overflow: hidden !important;
    width: 100% !important;
}
[data-testid="stChatMessage"] th {
    background: #dbeafe !important;
    color: #0f3460 !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
}
[data-testid="stChatMessage"] td {
    padding: 8px 14px !important;
    color: #0f2a45 !important;
}
[data-testid="stChatMessage"] tr:nth-child(even) td { background: #f5f9ff !important; }
[data-testid="stChatMessage"] tr:nth-child(odd)  td { background: #ffffff !important; }

/* ── SCROLLBAR ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #fde68a, #93c5fd);
    border-radius: 10px;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0);   }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "use_api" not in st.session_state:
    st.session_state.use_api = False


def _clear_chat() -> None:
    st.session_state.messages = []
    st.rerun()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("### ⚙️ Налаштування")
    st.session_state.use_api = st.toggle(
        "Use HTTP API", value=st.session_state.use_api,
        help=f"POST to {API_BASE_URL}/{CHAT_ENDPOINT}",
    )
    st.divider()
    st.markdown(
        f"**Режим:** {'🌐 FastAPI' if st.session_state.use_api else '⚡ Direct agent'}"
    )
    st.divider()
    if st.button("🗑 Очистити чат", use_container_width=True, key="clear_chat_sidebar"):
        _clear_chat()

use_api = st.session_state.use_api

# =========================================================
# MAIN
# =========================================================

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-wrap">
        <div class="welcome-icon">⚖️</div>
        <div class="welcome-title">Асистент з форфейтингу</div>
        <div class="welcome-sub">Розрахунки, схеми та аналіз форфейтингових операцій</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        avatar = "👩‍🎓" if message["role"] == "user" else "⚖️"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# =========================================================
# BACKEND
# =========================================================

def _extract_text(reply) -> str:
    if isinstance(reply, str):
        return reply
    if hasattr(reply, "content"):
        return "\n".join(
            block.text for block in reply.content if hasattr(block, "text")
        )
    if isinstance(reply, list):
        return "\n".join(
            item.get("text", "")
            for item in reply
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return str(reply)

def _chat_history() -> list[dict]:
    return st.session_state.messages[-MAX_CHAT_HISTORY:]


def _reset_async_caches() -> None:
    """MCP client and graph are tied to a closed loop — drop caches on loop recreate."""
    import src.agents.factory as factory
    import src.graph.supervisor as supervisor

    factory._client = None
    factory._all_tools = None
    factory._specialists.clear()
    supervisor._graph = None


def _run_async(coro):
    """Reuse one event loop across Streamlit reruns (asyncio.run closes the loop each time)."""
    loop = st.session_state.get("event_loop")
    if loop is None or loop.is_closed():
        _reset_async_caches()
        loop = asyncio.new_event_loop()
        st.session_state.event_loop = loop
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


async def _ask_direct(message: str, history: list[dict]) -> str:
    from src.agent import ask_agent
    return await ask_agent(message, history=history)

async def _ask_api(message: str, history: list[dict]) -> str:
    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(
            f"{API_BASE_URL}/{CHAT_ENDPOINT}",
            json={"message": message, "history": history},
        )
        resp.raise_for_status()
        return resp.json()["response"]

def get_assistant_reply(message: str, history: list[dict], use_api: bool) -> str:
    coro = _ask_api(message, history) if use_api else _ask_direct(message, history)
    raw = _run_async(coro)
    return _extract_text(raw)

# =========================================================
# INPUT
# =========================================================

# Повторне застосування після рендеру — перебиває inline-тему Streamlit
st.markdown("""
<style>
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div {
    background: transparent !important;
}
[data-testid="stChatInput"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1.5px solid rgba(147,197,253,0.8) !important;
    border-radius: 20px !important;
}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="textarea"] > div {
    background: #ffffff !important;
    background-color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

prompt = st.chat_input("Запитайте про форфейтингові операції...")

if prompt:
    history = _chat_history()
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👩‍🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Обчислюю..."):
            try:
                reply = get_assistant_reply(prompt, history, use_api)
            except httpx.HTTPError as exc:
                reply = f"❌ API error:\n\n`{exc}`"
            except Exception as exc:
                reply = f"❌ `{type(exc).__name__}: {exc}`"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()