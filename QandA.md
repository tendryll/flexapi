# Q&A

## Q: Is there a need to use request-scoped style over using a single-style global request for this application? Explain why.

Short answer: **yes — request-scoped sessions (what the app already does) are the correct choice, and a single global session would be actively buggy here.** Here's why.

### What the app currently does

In `app/config/database.py`:

```python
engine = create_async_engine(settings.database_url, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
```

The **engine** is a global singleton (correct — it owns the connection *pool* and is meant to be shared). But a fresh **`AsyncSession`** is created and torn down per request via the `get_session` dependency. That distinction is the key: share the engine, scope the session.

### Why a single global session breaks

A SQLAlchemy `Session`/`AsyncSession` is a stateful **unit of work** — it holds an identity map, pending/dirty objects, and a transaction. Sharing one across requests fails on several fronts:

**1. It is not concurrency-safe.**
`AsyncSession` is explicitly documented as *not* safe to share across concurrent tasks. FastAPI serves requests concurrently on one event loop. Two requests hitting one global session would interleave operations on the same connection/transaction and raise errors like `InterfaceError: another operation is in progress`, or silently corrupt each other's state.

**2. Shared transaction = cross-request contamination.**
A session wraps a transaction. With one global session, request A's `create_book` flush and request B's `update_book` live in the *same* transaction. A `commit()` from one flushes the other's half-finished work; a `rollback()` (e.g. the 422 path in `update_book`) discards a different request's changes. Requests must have independent transactional boundaries — that's exactly what per-request scoping gives.

**3. Shared identity map = stale data and memory growth.**
The session caches every loaded object in its identity map and keeps it until expiry/close. A long-lived global session accumulates every `Book`/`Author`/`Location` ever touched (a leak) and serves stale cached rows to later requests. Per-request sessions start clean and are discarded at the end.

**4. A poisoned session stays poisoned.**
Once an error puts a session into a failed state, it must be rolled back/discarded before reuse. A global session that errors would break *every subsequent request* until restart. A request-scoped session just gets thrown away.

### Why request scope is the natural fit

- A web request *is* the natural unit of work: open session → do work → commit/rollback → close. The `async with SessionLocal()` block maps one-to-one onto that lifecycle.
- The expensive resource — TCP connections to Postgres — is **already pooled and shared by the global engine**, so per-request sessions are cheap. You don't save anything meaningful by hoarding one session.
- It composes with FastAPI's DI and made testing trivial: `conftest.py` overrides `get_session` to swap in a per-test SQLite session without touching any business code.

### When a global/shared session *would* be fine

Essentially only single-threaded, single-task, serial usage: a one-shot CLI script, a migration, or a simple batch job with no concurrency. None of those describe a concurrent ASGI web service.

**Bottom line:** the engine is global (right), the session is request-scoped (right). Going to a single global session would trade nothing for guaranteed concurrency bugs, transaction bleed, and stale-cache problems. Keep it as is.

---

## Q: Should this project be updated to use a request-scope?

No. **The project is already request-scoped — there's nothing to change.** The code confirms it:

- **`get_session`** opens a brand-new `AsyncSession` via `async with SessionLocal()` on *every call*, and the `async with` block closes/rolls it back when the request finishes (including on exceptions). That is the definition of request scope.
- **`SessionDep`** wires that dependency into every endpoint, so each request gets its own isolated session. Every endpoint in `app/api/books.py` takes `session: SessionDep`, so there's no shared-session path anywhere.
- **`engine`** is the global singleton — which is exactly what *should* be global, since it owns the shared connection pool.

So the split is already the recommended one: **global engine, per-request session.** The earlier answer was describing the architecture this project already has, not a target to migrate toward.

### Nothing required, but two things worth knowing

1. **Transaction boundaries are explicit, not automatic.** Commits happen inside `crud.py` (`await session.commit()`), and the `async with` guarantees cleanup. This works correctly. If you ever wanted "one transaction per request, auto-commit at the end," you could switch to `async with SessionLocal.begin() as session:` and drop the manual commits — but that's a stylistic preference, not a fix. The current explicit style is perfectly valid and arguably clearer about where writes land.

2. **The only real "global session" risk would be accidental.** As long as no module creates a module-level `session = SessionLocal()` and reuses it, you're safe. Right now nothing does — sessions only ever come from the `get_session` dependency.

Bottom line: the request-scoped model is already in place and correctly implemented. No migration needed.
