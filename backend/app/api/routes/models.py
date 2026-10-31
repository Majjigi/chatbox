from fastapi import APIRouter

from app.providers.registry import list_models
from app.schemas.chat import ModelInfo

router = APIRouter(tags=["models"])


# GET /api/models — the choices for the model dropdown.
@router.get("/models")
def get_models() -> list[ModelInfo]:
    return list_models()
