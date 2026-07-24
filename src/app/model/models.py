"""Pydantic request/response models.

JSON field names from the spec (``isbn-10``, ``publishingDate``, ``pageCount``,
``postalCode``) are exposed via aliases. FastAPI serialises responses with
``by_alias=True`` by default, so the wire format matches the JSON Schema while
the Python attributes stay snake_case.
"""

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AddressIn(BaseModel):
    """Address as sent in the POST /book body (postalCode required)."""

    model_config = ConfigDict(populate_by_name=True)

    address1: str
    address2: str | None = None
    city: str
    province: str
    country: str
    postal_code: str = Field(alias="postalCode")


class AddressOut(BaseModel):
    """Address as returned in responses (postalCode may be null in storage)."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    address1: str
    address2: str | None = None
    city: str
    province: str
    country: str
    postal_code: str | None = Field(default=None, alias="postalCode")


class BookCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    description: str
    authors: list[str] = Field(min_length=1)
    isbn_10: str | None = Field(default=None, alias="isbn-10")
    isbn_13: str | None = Field(default=None, alias="isbn-13")
    publisher: str
    publishing_date: date = Field(alias="publishingDate")
    page_count: int = Field(alias="pageCount")
    location: AddressIn | None = None
    availability: bool | None = None

    @field_validator("authors")
    @classmethod
    def _authors_unique(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("authors must be unique")
        return value


class BookUpdate(BaseModel):
    """PUT /book/{id} body.

    ``location`` is the UUID of an existing ``location`` row (per the spec it is
    a plain string, unlike the address object used on create). Unset fields are
    left unchanged; explicit ``null`` clears the value.
    """

    model_config = ConfigDict(populate_by_name=True)

    location: str | None = None
    availability: bool | None = None


class BookResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: uuid.UUID
    title: str
    description: str
    authors: list[str]
    isbn_10: str | None = Field(default=None, alias="isbn-10")
    isbn_13: str | None = Field(default=None, alias="isbn-13")
    publisher: str
    publishing_date: date = Field(alias="publishingDate")
    page_count: int = Field(alias="pageCount")
    location: AddressOut | None = None
    availability: bool | None = None
