from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness check; it intentionally has no database dependency."""
    return {"status": "ok"}
