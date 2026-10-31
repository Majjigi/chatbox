# ChatBox — Backend

A Python API built with [FastAPI](https://fastapi.tiangolo.com/).

## Project structure

```
backend/
├── app/
│   ├── main.py              # Creates the FastAPI app and plugs in the routes
│   ├── core/
│   │   └── config.py        # Settings loaded from env / .env
│   └── api/
│       └── routes/
│           └── health.py    # GET /api/health
├── tests/
│   └── test_health.py
├── requirements.txt         # Packages the app needs
├── requirements-dev.txt     # + packages for testing
└── .env.example             # Sample settings — copy to .env
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

## Run the server

```bash
uvicorn app.main:app --reload --reload-dir app
```

- Health check: http://localhost:8000/api/health → `{"status": "ok"}`
- Interactive docs (Swagger): http://localhost:8000/docs — try every endpoint from the browser

`--reload` restarts the server when you save a file. Changes to `.env` need a manual restart
(`Ctrl+C`, then run the command again).

## Run the tests

```bash
pytest
```
