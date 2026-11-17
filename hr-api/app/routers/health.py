from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness check")
async def health() -> dict[str, str]:
    """Returns ok when the server is up."""
    return {"status": "ok"}
