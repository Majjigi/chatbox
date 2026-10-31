# Phase 1 — Backend foundation

**Goal:** a running FastAPI server with one endpoint, ready for the chat features to be added.

## What was built

| File | What it does |
| ---- | ------------ |
| `backend/app/main.py` | Creates the FastAPI `app`, turns on CORS, and plugs in the routes |
| `backend/app/core/config.py` | Reads settings from `.env` (later: the API keys) |
| `backend/app/api/routes/health.py` | `GET /api/health` → `{"status": "ok"}` |
| `backend/tests/test_health.py` | Checks the health endpoint works |
| `backend/.env.example` | Sample settings file — copied to `.env` |

## Key ideas

### FastAPI routes

A *route* connects a URL to a Python function:

```python
@router.get("/health")          # when someone sends GET /health …
def health_check() -> dict[str, str]:
    return {"status": "ok"}     # … run this and send the result back as JSON
```

The `@router.get(...)` line above the function is a **decorator**: it registers the function
with FastAPI without changing what the function does.

### Settings from `.env`

`Settings` in `config.py` is a class whose fields have default values. `pydantic-settings`
replaces each default with the matching environment variable or `.env` line if one exists.
This keeps secrets (like API keys in phase 3) out of the code — `.env` is listed in
`.gitignore`, so it is never committed.

### CORS

The Angular app will run at `http://localhost:4200` and the API at `http://localhost:8000`.
Different ports count as different "origins", and browsers block cross-origin requests unless
the server says they're allowed. `CORSMiddleware` in `main.py` adds that permission for the
origins listed in `cors_origins`.

## Try it

```bash
cd backend
uvicorn app.main:app --reload --reload-dir app
```

Open http://localhost:8000/api/health and http://localhost:8000/docs.

Run the tests with `pytest`.

## Next

[Phase 2](phase-2-streaming-demo-model.md) adds the streaming chat endpoint.
