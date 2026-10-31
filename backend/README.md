# ChatBox — Backend

A Python API built with [FastAPI](https://fastapi.tiangolo.com/).

## Project structure

```
backend/
├── app/
│   ├── main.py                  # Creates the FastAPI app and plugs in the routes
│   ├── core/
│   │   └── config.py            # Settings loaded from env / .env
│   ├── schemas/
│   │   └── chat.py              # Shapes of requests, responses and stream events
│   ├── providers/               # One class per AI service, all with the same method
│   │   ├── base.py              # ChatProvider: the common template
│   │   ├── gemini_provider.py   # Google Gemini (google-genai SDK)
│   │   ├── claude_provider.py   # Anthropic Claude (anthropic SDK)
│   │   ├── demo_provider.py     # Offline pretend model (no API key needed)
│   │   └── registry.py          # The list of models + "give me the provider for X"
│   └── api/
│       └── routes/
│           ├── health.py        # GET  /api/health
│           ├── models.py        # GET  /api/models
│           └── chat.py          # POST /api/chat/stream  (streams the reply)
├── tests/                       # pytest tests — no real API calls
├── requirements.txt             # Packages the app needs
├── requirements-dev.txt         # + packages for testing
└── .env.example                 # Sample settings — copy to .env
```

## Setup

Requires Python 3.10 or newer. On Windows, use `py` instead of `python` if `python` isn't on
your PATH.

```bash
cd backend

# 1. Create a virtual environment (a private folder of packages for this project)
python -m venv .venv

# 2. Activate it
.venv\Scripts\Activate.ps1      # Windows (PowerShell)
source .venv/bin/activate       # macOS / Linux

# 3. Install the packages
pip install -r requirements-dev.txt

# 4. Create your local settings file
cp .env.example .env
```

> **Using [uv](https://docs.astral.sh/uv/) instead of pip?** `uv venv` then
> `uv pip install -r requirements-dev.txt` does steps 1–3 in one go.

### Add your API keys

Open `backend/.env` and paste in a key for each model you want to use:

| Setting | Where to get it |
| ------- | --------------- |
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey |
| `ANTHROPIC_API_KEY` | https://platform.claude.com |

A model without a key stays in the dropdown but is greyed out. The **Demo model** always works,
with no key at all. You can also change which model is used with `GEMINI_MODEL` and
`CLAUDE_MODEL`.

## Run the server

```bash
uvicorn app.main:app --reload --reload-dir app
```

- Health check: http://localhost:8000/api/health → `{"status": "ok"}`
- Interactive docs (Swagger): http://localhost:8000/docs — try every endpoint from the browser

`--reload` restarts the server when you save a file. Changes to `.env` need a manual restart
(`Ctrl+C`, then run the command again).

> **Windows note:** if the log says `Reloading...` but your change doesn't show up (no
> `Application startup complete` line follows), the auto-reload got stuck. Press `Ctrl+C` and
> start the server again.

## API endpoints

| Method | URL                | What it does                                            |
| ------ | ------------------ | ------------------------------------------------------- |
| `GET`  | `/api/health`      | Check the server is running                             |
| `GET`  | `/api/models`      | List the models for the dropdown (and which are usable) |
| `POST` | `/api/chat/stream` | Send the conversation, get the reply as a live stream   |

`POST /api/chat/stream` body:

```json
{
  "model": "demo",
  "system_prompt": "You are a helpful assistant.",
  "messages": [
    { "role": "user", "content": "Hi!" },
    { "role": "assistant", "content": "Hello! How can I help?" },
    { "role": "user", "content": "Tell me a joke." }
  ]
}
```

The response is a stream of [Server-Sent Events](../docs/phases/phase-2-streaming-demo-model.md):
many `token` events, then one `done` event with the token counts and timings (or an `error`
event if something fails).

Try it from a terminal (`-N` shows events as they arrive):

```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"model": "demo", "messages": [{"role": "user", "content": "Hi!"}]}'
```

## Run the tests

```bash
pytest
```
