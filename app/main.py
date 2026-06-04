"""FastAPI application entry point."""

from fastapi import FastAPI

from .api import books

app = FastAPI(title="Library API", version="0.1.0")
app.include_router(books.router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
