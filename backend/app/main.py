"""
Entry point of the backend. Run it with:

    uvicorn app.main:app --reload --reload-dir app

`app.main:app` means "in the file app/main.py, use the variable called `app`".
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, health, models
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.version)

# The Angular app runs on a different port (4200) than this API (8000).
# Browsers block such "cross-origin" calls unless the API allows them — CORS does that.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Plug each group of routes into the app, all under /api.
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(models.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)
