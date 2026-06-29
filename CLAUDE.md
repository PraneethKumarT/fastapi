# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency and environment management.

```bash
uv sync                          # install/sync dependencies into .venv
uv run fastapi dev main.py       # run dev server with auto-reload (http://127.0.0.1:8000)
uv run fastapi run main.py       # run production server
uv add <package>                 # add a dependency (updates pyproject.toml + uv.lock)
```

Interactive API docs are served at `/docs` (Swagger) and `/redoc`.

There is no test suite, linter, or migration tool configured. The SQLite schema is created automatically at startup via `Base.metadata.create_all` — there is no Alembic. Changing a model does **not** migrate an existing `fastapi_blog.db`; delete the DB file to recreate the schema during development.

## Architecture

A FastAPI blog serving both server-rendered HTML pages and a JSON REST API from the same app, backed by SQLite via SQLAlchemy 2.0 (ORM with typed `Mapped[...]` columns).

**Module layout** — flat, single-package:
- `main.py` — all routes, app setup, and exception handlers (no router modules)
- `models.py` — SQLAlchemy ORM models (`User`, `Post`)
- `schemas.py` — Pydantic request/response models
- `database.py` — engine, `SessionLocal`, `Base`, and the `get_db` dependency
- `templates/` — Jinja2 templates; `home.html`/`post.html`/`error.html` all `{% extends "layout.html" %}`
- `static/` — CSS and images, mounted at `/static`
- `snippets.txt` — scratch/reference file, not imported by the app

**HTML vs API split.** Routes under `/api/...` return JSON (validated through Pydantic `*Response` schemas); all other routes render Jinja2 templates. This split is enforced in the exception handlers in `main.py`: `StarletteHTTPException` and `RequestValidationError` are caught globally and dispatched by `request.url.path.startswith("/api")` — API errors become JSON, page errors render `error.html`. When adding routes, keep this prefix convention so errors render correctly.

**DB session injection.** Routes take `db: DbSession`, an `Annotated[Session, Depends(get_db)]` alias defined in `main.py`. `get_db` yields a session from a context manager so it closes per-request. Use `db.get(Model, id)` / `db.scalars(select(...))` (SQLAlchemy 2.0 style). The `find_post` / `find_user` helpers centralize the 404-on-missing pattern — reuse them rather than re-checking inline.

**Models & relationships.** `User` 1‑to‑many `Post` via `back_populates`, with `cascade="all, delete-orphan"` so deleting a user deletes their posts. `Post.date_posted` is set by the DB (`server_default=func.now()`).

**Schema conventions** (`schemas.py`):
- Response models set `model_config = ConfigDict(from_attributes=True)` to serialize ORM objects directly.
- `PostResponse.author` uses `Field(validation_alias="user")` to expose the ORM `user` relationship as `author` in JSON.
- `*Update` schemas make every field `Optional`; routes apply them with `model_dump(exclude_unset=True)` so only provided fields are patched (PATCH semantics).
- Passwords are stored and accepted in plaintext — there is no hashing/auth layer yet.

## Known gaps

- `main.py` mounts `/media` from a `media/` directory that does not exist in the repo; the app will fail to start until that directory exists (create it or remove the mount).
- No authentication — `post_author` links and user identity are placeholders.
