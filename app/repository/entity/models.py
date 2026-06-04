"""SQLAlchemy ORM models mapping the library schema.

Note on column names: the DDL declares some columns with unquoted mixed case
(``postalCode``, ``publishingDate``). PostgreSQL folds unquoted identifiers to
lower case, so the real column names are ``postalcode`` / ``publishingdate``.
Those are mapped explicitly below.
"""

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils.compat import uuid7

from ...config.database import Base


class Author(Base):
    __tablename__ = "author"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    author: Mapped[str] = mapped_column(Text, nullable=False)


class Location(Base):
    __tablename__ = "location"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    address1: Mapped[str] = mapped_column(Text, nullable=False)
    address2: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str] = mapped_column(Text, nullable=False)
    province: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str] = mapped_column(Text, nullable=False)
    postal_code: Mapped[str | None] = mapped_column("postalcode", Text)


class Book(Base):
    __tablename__ = "book"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Mirrors the DDL: book.author_id is NOT NULL. It is set to the first author;
    # the full author list lives in the book_author junction table.
    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    isbn_10: Mapped[str | None] = mapped_column(Text)
    isbn_13: Mapped[str | None] = mapped_column(Text)
    publisher: Mapped[str] = mapped_column(Text, nullable=False)
    publishing_date: Mapped[date] = mapped_column("publishingdate", Date, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    location_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("location.id"))
    availability: Mapped[bool | None] = mapped_column(Boolean, default=False)

    location: Mapped[Location | None] = relationship(lazy="selectin")
    authors: Mapped[list[Author]] = relationship(
        secondary="book_author",
        lazy="selectin",
        order_by="Author.author",
    )


class BookAuthor(Base):
    __tablename__ = "book_author"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid7)
    author_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("author.id"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("book.id"), nullable=False)
