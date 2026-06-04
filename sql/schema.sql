-- Canonical PostgreSQL schema for the library application.
-- uuidv7() is built in on PostgreSQL 18+. On earlier versions install an
-- extension such as pg_uuidv7, or rely on the application to supply ids
-- (the app generates UUIDv7 values itself, so the DB default is optional).

CREATE TABLE author (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    author text NOT NULL
);

CREATE TABLE location (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    address1 text NOT NULL,
    address2 text,
    city text NOT NULL,
    province text NOT NULL,
    country text NOT NULL,
    postalCode text
);

CREATE TABLE book (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    title text NOT NULL,
    description text NOT NULL,
    author_id UUID NOT NULL,
    isbn_10 text,
    isbn_13 text,
    publisher text NOT NULL,
    publishingDate date NOT NULL,
    page_count int NOT NULL,
    location_id UUID,
    availability boolean DEFAULT false,

    CONSTRAINT fk_book_location FOREIGN KEY (location_id) REFERENCES location (id)
);

CREATE TABLE book_author (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    author_id UUID NOT NULL,
    book_id UUID NOT NULL,

    CONSTRAINT fk_book_author_author FOREIGN KEY (author_id) references author (id),
    CONSTRAINT fk_book_author_book FOREIGN KEY (book_id) references book (id)
);
