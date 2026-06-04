"""Data-access / persistence logic for books."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model.models import Author, Book, BookAuthor, Location
from .schemas import BookCreate, BookUpdate


class InvalidLocationError(Exception):
    """Raised when a PUT location value is not a valid UUID."""


class LocationNotFoundError(Exception):
    """Raised when a PUT location UUID does not reference an existing row."""


async def _get_or_create_author(session: AsyncSession, name: str) -> Author:
    result = await session.execute(select(Author).where(Author.author == name))
    author = result.scalar_one_or_none()
    if author is None:
        author = Author(author=name)
        session.add(author)
        await session.flush()
    return author


async def get_book(session: AsyncSession, book_id: uuid.UUID) -> Book | None:
    result = await session.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def create_book(session: AsyncSession, data: BookCreate) -> Book:
    # Deduplicate while preserving order; reuse existing author rows by name.
    authors: list[Author] = []
    seen: set[str] = set()
    for name in data.authors:
        if name in seen:
            continue
        seen.add(name)
        authors.append(await _get_or_create_author(session, name))

    location: Location | None = None
    if data.location is not None:
        location = Location(
            address1=data.location.address1,
            address2=data.location.address2,
            city=data.location.city,
            province=data.location.province,
            country=data.location.country,
            postal_code=data.location.postal_code,
        )
        session.add(location)
        await session.flush()

    book = Book(
        title=data.title,
        description=data.description,
        author_id=authors[0].id,
        isbn_10=data.isbn_10,
        isbn_13=data.isbn_13,
        publisher=data.publisher,
        publishing_date=data.publishing_date,
        page_count=data.page_count,
        location_id=location.id if location is not None else None,
        availability=bool(data.availability),
    )
    session.add(book)
    await session.flush()

    for author in authors:
        session.add(BookAuthor(author_id=author.id, book_id=book.id))

    await session.commit()
    refreshed = await get_book(session, book.id)
    assert refreshed is not None  # just-committed row must exist
    return refreshed


async def update_book(session: AsyncSession, book_id: uuid.UUID, data: BookUpdate) -> Book | None:
    book = await get_book(session, book_id)
    if book is None:
        return None

    fields = data.model_dump(exclude_unset=True)

    if "availability" in fields:
        book.availability = fields["availability"]

    if "location" in fields:
        raw = fields["location"]
        if raw is None:
            book.location_id = None
        else:
            try:
                location_id = uuid.UUID(raw)
            except (ValueError, AttributeError) as exc:
                raise InvalidLocationError(raw) from exc
            location = await session.get(Location, location_id)
            if location is None:
                raise LocationNotFoundError(raw)
            book.location_id = location.id

    await session.commit()
    return await get_book(session, book_id)


async def delete_book(session: AsyncSession, book_id: uuid.UUID) -> bool:
    # Load via get_book so the authors collection is populated; deleting the
    # book then lets SQLAlchemy remove the book_author association rows.
    book = await get_book(session, book_id)
    if book is None:
        return False
    await session.delete(book)
    await session.commit()
    return True
