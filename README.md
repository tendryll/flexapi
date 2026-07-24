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
src/app/
├── api/                    # HTTP layer (FastAPI routers)
│   └── books.py
├── service/                # business logic
│   └── service.py
├── repository/             # persistence layer
│   ├── book_repository.py  # data access / queries
│   └── entity/             # SQLAlchemy ORM entities
│       └── models.py
├── model/                  # Pydantic request/response models
│   └── models.py
├── config/                 # settings + database engine/session
│   ├── config.py
│   └── database.py
└── main.py                 # app entry point
```

Request flow: `api` → `service` → `repository` → `entity`.

## Setup

```bash
uv sync                       # create venv + install deps
cp .env.example .env          # configure DATABASE_URL
docker compose up db flyway   # Postgres 18 + Flyway runs the migrations
uv run uvicorn app.main:app --reload --app-dir src
```

The database schema and seed data are managed by [Flyway](https://flyway.org/).
Migrations live in [`flyway/sql/`](flyway/sql/):

| Script                       | Purpose                                  |
| ---------------------------- | ---------------------------------------- |
| `V1__create_tables.sql`      | Creates the `author`/`location`/`book`/`book_author` tables |
| `V2__insert_mock_data.sql`   | Seeds mock authors, locations and books  |

The `flyway` Compose service waits for Postgres to become healthy, applies any
outstanding migrations, then exits. Re-running `docker compose up flyway` is
safe — Flyway only applies versions not already recorded in
`flyway_schema_history`. [`sql/schema.sql`](sql/schema.sql) is retained as a
plain-SQL reference copy of the DDL.

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
