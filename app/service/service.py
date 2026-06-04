"""Business logic for book operations.

Sits between the API layer (``app.api``) and the persistence layer
(``app.crud``): it turns ORM rows into response models and raises domain
exceptions for not-found conditions, keeping HTTP concerns out of this layer.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud
from ..crud import InvalidLocationError, LocationNotFoundError
from ..model.models import Book
from ..schemas import AddressOut, BookCreate, BookResponse, BookUpdate

__all__ = [
    "BookNotFoundError",
    "InvalidLocationError",
    "LocationNotFoundError",
    "create_book",
    "delete_book",
    "get_book",
    "update_book",
]


class BookNotFoundError(Exception):
    """Raised when a book id does not reference an existing row."""


def _serialize(book: Book) -> BookResponse:
    # Built via model_validate (populate_by_name) so snake_case attribute names
    # map onto the alias-bearing response fields.
    return BookResponse.model_validate(
        {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "authors": [author.author for author in book.authors],
            "isbn_10": book.isbn_10,
            "isbn_13": book.isbn_13,
            "publisher": book.publisher,
            "publishing_date": book.publishing_date,
            "page_count": book.page_count,
            "location": AddressOut.model_validate(book.location) if book.location else None,
            "availability": book.availability,
        }
    )


async def create_book(session: AsyncSession, payload: BookCreate) -> BookResponse:
    book = await crud.create_book(session, payload)
    return _serialize(book)


async def get_book(session: AsyncSession, book_id: uuid.UUID) -> BookResponse:
    book = await crud.get_book(session, book_id)
    if book is None:
        raise BookNotFoundError(book_id)
    return _serialize(book)


async def update_book(
    session: AsyncSession, book_id: uuid.UUID, payload: BookUpdate
) -> BookResponse:
    book = await crud.update_book(session, book_id, payload)
    if book is None:
        raise BookNotFoundError(book_id)
    return _serialize(book)


async def delete_book(session: AsyncSession, book_id: uuid.UUID) -> None:
    deleted = await crud.delete_book(session, book_id)
    if not deleted:
        raise BookNotFoundError(book_id)
