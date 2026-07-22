"""SQLModel table models mapping the library schema.

Note on column names: the DDL declares some columns with unquoted mixed case
(``postalCode``, ``publishingDate``). PostgreSQL folds unquoted identifiers to
lower case, so the real column names are ``postalcode`` / ``publishingdate``.
Those are mapped explicitly below via ``sa_column``.
"""

import uuid
from datetime import date

from sqlalchemy import Column, Date, Text
from sqlmodel import Field, Relationship, SQLModel
from uuid_utils.compat import uuid7


class Author(SQLModel, table=True):
    __tablename__ = "author"

    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    author: str


class Location(SQLModel, table=True):
    __tablename__ = "location"

    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    address1: str
    address2: str | None = None
    city: str
    province: str
    country: str
    postal_code: str | None = Field(default=None, sa_column=Column("postalcode", Text))


class Book(SQLModel, table=True):
    __tablename__ = "book"

    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    title: str
    description: str
    # the full author list lives in the book_author junction table.
    isbn_10: str | None = None
    isbn_13: str | None = None
    publisher: str
    publishing_date: date = Field(sa_column=Column("publishingdate", Date, nullable=False))
    page_count: int
    location_id: uuid.UUID | None = Field(default=None, foreign_key="location.id")
    availability: bool | None = False

    location: Location | None = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    authors: list[Author] = Relationship(
        sa_relationship_kwargs={
            "secondary": "book_author",
            "lazy": "selectin",
            "order_by": "Author.author",
        },
    )


class BookAuthor(SQLModel, table=True):
    __tablename__ = "book_author"

    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    author_id: uuid.UUID = Field(foreign_key="author.id")
    book_id: uuid.UUID = Field(foreign_key="book.id")
