# Forfaiting-Multi-Agent

Requires **Python 3.11–3.13** (`uv sync` uses `.python-version`). LangChain is not compatible with Python 3.14 yet.

## Run MCP server

```bash
uv run server.py
```

## Run HTTP API (LangGraph)

```bash
uv run python -m uvicorn src.api.chat:app --host 0.0.0.0 --port 8000 --reload

http://127.0.0.1:8000/docs
```

### Endpoints

- `POST /chat` - LangGraph supervisor (auto-routes to a specialist)
- `POST /orchestrate` - discounting specialist only

Compare routes (via `/chat`):
- **schema_compare** — Scheme 1 + Scheme 2 in parallel, then synthesis node
- **discount_compare** — straight discount + discount-to-yield in parallel, then synthesis

## Run Streamlit chat UI

With MCP server running:

```bash
uv run streamlit run streamlit_app.py
```

Optional: enable **Use HTTP API** in the sidebar if you prefer calling FastAPI instead of in-process agents.

Set `FORFAITING_API_URL` (default `http://127.0.0.1:8000`) when using API mode.

### Discounting formulas

- Straight Discount Factor = `1 - (r/100) * (D/360)`
- Annual Yield Factor = `(1 + Y/100)^N * (1 + (Y/100) * (D/360))`
- Where `N` is full years and `D` is additional days

### Manager Routing

`/orchestrate` uses a manager step (LangGraph router) that chooses one tool:
- `straight_discounting`
- `yield_discounting`

Pass routing intent in `user_query` (for example: "calculate by yield" or "use straight discount").