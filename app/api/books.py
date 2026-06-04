"""/book endpoints — thin HTTP layer delegating to the service."""

import uuid

from fastapi import APIRouter, HTTPException, status

from ..config.database import SessionDep
from ..schemas import BookCreate, BookResponse, BookUpdate
from ..service import service

router = APIRouter(prefix="/book", tags=["books"])


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(payload: BookCreate, session: SessionDep) -> BookResponse:
    return await service.creatShoue_book(session, payload)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: uuid.UUID, session: SessionDep) -> BookResponse:
    try:
        return await service.get_book(session, book_id)
    except service.BookNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found") from exc


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(book_id: uuid.UUID, payload: BookUpdate, session: SessionDep) -> BookResponse:
    try:
        return await service.update_book(session, book_id, payload)
    except service.InvalidLocationError as exc:
        raise HTTPException(422, detail="location must be a valid location UUID") from exc
    except service.LocationNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="location not found") from exc
    except service.BookNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found") from exc


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: uuid.UUID, session: SessionDep) -> None:
    try:
        await service.delete_book(session, book_id)
    except service.BookNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found") from exc
