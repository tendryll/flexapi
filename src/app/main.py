"""FastAPI application entry point."""

from fastapi import FastAPI

from .routes import book, location

app = FastAPI(title="Library API", version="0.1.0")
app.include_router(book.router)
app.include_router(location.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Report that the service is up (no dependency checks)."""
    return {"status": "ok"}
