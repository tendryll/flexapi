# flexapi — Library API

A FastAPI + Pydantic + SQLModel (async SQLAlchemy) service for managing library
books, backed by PostgreSQL. Dependencies are managed with
[uv](https://docs.astral.sh/uv/), linting/formatting with
[Ruff](https://docs.astral.sh/ruff/), and type checking with
[ty](https://github.com/astral-sh/ty).

## Endpoints

| Method | Path         | Success | Description                                    |
| ------ | ------------ | ------- | ---------------------------------------------- |
| POST   | `/book`      | 201     | Create a book (with authors + location)        |
| GET    | `/book/{id}` | 200     | Fetch a book                                   |
| PUT    | `/book/{id}` | 200     | Update `availability` and/or `location` (UUID) |
| DELETE | `/book/{id}` | 204     | Delete a book                                  |
| GET    | `/health`    | 200     | Liveness check                                 |

Interactive docs are served at `/docs` once running.

JSON field names follow the spec (`isbn-10`, `isbn-13`, `publishingDate`,
`pageCount`, `postalCode`) via Pydantic aliases; Python attributes stay
snake_case.

## Layout

```
src/app/
├── routes/                 # HTTP layer (FastAPI routers)
│   └── books.py
├── service/                # business logic + domain exceptions
│   └── service.py
├── data/                   # persistence layer
│   ├── book_repository.py  # data access / queries
│   └── entity/             # SQLModel table models
│       └── models.py
├── model/                  # Pydantic request/response models
│   └── models.py
├── config/                 # settings + database engine/session
│   ├── config.py
│   └── database.py
└── main.py                 # app entry point
```

Request flow: `routes` → `service` → `data` → `entity`. The service layer raises
domain exceptions (`BookNotFoundError`, `InvalidLocationError`,
`LocationNotFoundError`) that `routes` translates into HTTP status codes, so
HTTP concerns stay out of the lower layers.

Note that `src/app/data/` (the persistence layer) is distinct from the
top-level `data/` directory, which holds container fixtures for Flyway and
WireMock.

## Setup

```bash
uv sync                       # create venv + install deps
cp .env.example .env          # configure DATABASE_URL
docker compose up db flyway   # Postgres 18 + Flyway runs the migrations
uv run uvicorn app.main:app --reload --app-dir src
```

The database schema and seed data are managed by [Flyway](https://flyway.org/).
Migrations live in [`data/flyway/sql/`](data/flyway/sql/):

| Script                     | Purpose                                                     |
| -------------------------- | ----------------------------------------------------------- |
| `V1__create_tables.sql`    | Creates the `author`/`location`/`book`/`book_author` tables |
| `V2__insert_mock_data.sql` | Seeds mock authors, locations and books                     |

The `flyway` Compose service waits for Postgres to become healthy, applies any
outstanding migrations, then exits. Re-running `docker compose up flyway` is
safe — Flyway only applies versions not already recorded in
`flyway_schema_history`. [`sql/schema.sql`](sql/schema.sql) is retained as a
plain-SQL reference copy of the DDL.

Compose also defines a `wiremock` service (port 8080) stubbing a `GET /location`
endpoint. It is scaffolding for a future upstream location service — nothing in
the app calls it yet.

## Tooling

```bash
uv run ruff check .           # lint
uv run ruff format .          # format
uv run ty check               # type check
uv run pytest                 # unit tests
uv run behave                 # integration tests (Gherkin)
```

Both test suites run the ASGI app against an in-memory SQLite database with
`get_session` overridden, so no PostgreSQL instance is required:

- **Unit** — [`tests/unit/`](tests/unit/), pytest with `asyncio_mode = "auto"`.
- **Integration** — [`tests/integration/`](tests/integration/), Behave driving
  [`books.feature`](tests/integration/books.feature) through the real HTTP
  surface. Each scenario gets a fresh database seeded with a known book;
  request bodies come from [`tests/resources/`](tests/resources/).

## Design notes

- **Authors via `book_author`** — a book's authors live entirely in the
  `book_author` junction table; `book` itself carries no author column. The
  repository resolves author names to `author` rows (reusing existing ones) and
  writes the junction entries.
- **PUT `location`** — per the spec this is a plain `string`, not an address
  object. It is treated as the UUID of an existing `location` row (invalid UUID
  → 422, unknown UUID → 404). Send `null` to clear it. On create, `location` is
  a full address object instead.
- **UUIDv7** — `uuidv7()` is native to PostgreSQL 18+. The app also generates
  UUIDv7 ids itself (`uuid-utils`), so it works on older Postgres too.
- **Column casing** — unquoted `postalCode`/`publishingDate` in the DDL fold to
  `postalcode`/`publishingdate` in Postgres; the ORM maps these explicitly via
  `sa_column`.

## License

[MIT](LICENSE)