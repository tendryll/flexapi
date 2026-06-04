# flexapi — Library API

A FastAPI + Pydantic + SQLAlchemy (async) service for managing library books,
backed by PostgreSQL. Dependencies are managed with [uv](https://docs.astral.sh/uv/),
linting/formatting with [Ruff](https://docs.astral.sh/ruff/), and type checking
with [ty](https://github.com/astral-sh/ty).

## Endpoints

| Method | Path          | Description                                   |
| ------ | ------------- | --------------------------------------------- |
| POST   | `/book`       | Create a book (with authors + location)       |
| GET    | `/book/{id}`  | Fetch a book                                  |
| PUT    | `/book/{id}`  | Update `availability` and/or `location` (UUID)|
| DELETE | `/book/{id}`  | Delete a book                                 |
| GET    | `/health`     | Liveness check                                |

Interactive docs are served at `/docs` once running.

## Layout

```
app/
├── api/        # HTTP layer (FastAPI routers)
│   └── books.py
├── service/    # business logic
│   └── service.py
├── crud.py     # data access / persistence
├── model/      # SQLAlchemy ORM models
│   └── models.py
├── config/     # settings + database engine/session
│   ├── config.py
│   └── database.py
├── schemas.py  # Pydantic request/response models
└── main.py     # app entry point
```

Request flow: `api` → `service` → `crud` → `model`.

## Setup

```bash
uv sync                       # create venv + install deps
cp .env.example .env          # configure DATABASE_URL
docker compose up -d db       # Postgres 18 with schema auto-loaded
uv run uvicorn app.main:app --reload
```

The schema is in [`sql/schema.sql`](sql/schema.sql) and is loaded automatically
by the Compose Postgres container on first start.

## Tooling

```bash
uv run ruff check .           # lint
uv run ruff format .          # format
uv run ty check               # type check
uv run pytest                 # tests (in-memory SQLite, no DB needed)
```

## Design notes

- **`book.author_id` vs `book_author`** — the DDL keeps a `NOT NULL author_id`
  on `book` *and* a `book_author` junction table. The app writes all authors to
  `book_author` and sets `book.author_id` to the first author.
- **PUT `location`** — per the spec this is a plain `string`, not an address
  object. It is treated as the UUID of an existing `location` row (invalid UUID
  → 422, unknown UUID → 404). Send `null` to clear it.
- **UUIDv7** — `uuidv7()` is native to PostgreSQL 18+. The app also generates
  UUIDv7 ids itself (`uuid-utils`), so it works on older Postgres too.
- **Column casing** — unquoted `postalCode`/`publishingDate` in the DDL fold to
  `postalcode`/`publishingdate` in Postgres; the ORM maps these explicitly.
