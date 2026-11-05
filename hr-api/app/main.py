from fastapi import FastAPI

app = FastAPI(
    title="HR API",
    description="Employees, departments and leave for a small company.",
    version="0.1.0",
)


@app.get("/health", summary="Liveness check")
async def health() -> dict[str, str]:
    """Returns ok when the server is up."""
    return {"status": "ok"}