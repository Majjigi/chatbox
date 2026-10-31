from fastapi import APIRouter

router = APIRouter(tags=["health"])


# GET /api/health — a tiny endpoint to check the server is up.
@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
