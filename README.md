# Forfaiting-Multi-Agent

## Run MCP server

```bash
uv run python server.py
```

## Run HTTP API (LangGraph)

```bash
uv run python api_server.py
```

### Endpoints

- `POST /orchestrate` - manager endpoint that selects one discounting tool

### Discounting formulas

- Straight Discount Factor = `1 - (r/100) * (D/360)`
- Annual Yield Factor = `(1 + Y/100)^N * (1 + (Y/100) * (D/360))`
- Where `N` is full years and `D` is additional days

### Manager Routing

`/orchestrate` uses a manager step (LangGraph router) that chooses one tool:
- `straight_discounting`
- `yield_discounting`

Pass routing intent in `user_query` (for example: "calculate by yield" or "use straight discount").