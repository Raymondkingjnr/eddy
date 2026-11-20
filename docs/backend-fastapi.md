# Backend guide: Python and FastAPI

This guide covers the current backend prototype and conventions for adding
Lesson Mentor features. Target architecture below does not imply that missing
features already exist.

## 1. Current stack and layout

- Python `>=3.11,<3.14`
- FastAPI and FastAPI Users
- Pydantic and `pydantic-settings`
- SQLAlchemy async ORM and `asyncpg` for PostgreSQL
- Alembic for schema migrations
- `uv` lockfile and `requirements.txt`

Current source layout:

```text
backend/
  main.py
  config/
    config.py
    db.py
    db_config.py
  models/models.py
  schemas.py
  users/
    users.py
    router.py
    service.py
  api/
    lesson/
      router.py
      service.py
  seed.py
  alembic/
    env.py
    versions/
  pyproject.toml
  requirements.txt
```

`main.py` creates the FastAPI application and mounts authentication,
user-management, and lesson routers. Models currently represent User, Lesson,
and Topic. The lesson module is read-only for now (see section 4). There is no
lesson write endpoint, project resource router/service, Project model, or AI
generation integration yet.

## 2. Local setup

Run commands from `backend/`. Install the locked Python dependencies:

```sh
uv sync
```

Configure a `DATABASE_URL` for the PostgreSQL database and a strong `JWT_SECRET`
in the local environment. `config/config.py` reads settings from environment
variables and a `.env` file. Set `FRONTEND_URL` to the allowed frontend origin
or comma-separated origins when the browser calls the API directly; local Vite
development uses a proxy. Keep `.env` local and never commit its contents.

Start the development API:

```sh
uv run fastapi dev main.py
```

The FastAPI interactive documentation is available at `/docs` while the local
server is running.

## 3. Router and service boundaries

The lesson feature lives in `modules/lesson/`; user routes remain under
`users/`. Add each new feature with its own router and service rather than
growing `main.py` or `users/users.py` into a collection of unrelated
endpoints:

```text
backend/
  modules/
    lesson/
      router.py
      service.py
    project/
      router.py
      service.py
    ai_generation/
      router.py
      service.py
```

Only `modules/lesson/` exists today; `project/` and `ai_generation/` are the
recommended structure for future modules, not current files. Keep shared database models, settings, and schemas reusable and
organized with the existing `models/`, `config/`, and `schemas.py` until an
implementation change justifies moving them.

### `router.py`

- Define REST endpoints and their request/response contracts.
- Inject the asynchronous database session and authenticated user through FastAPI
  dependencies.
- Use Pydantic schemas for validation and response serialization.
- Translate known domain outcomes into clear HTTP status codes and responses.
- Keep database queries and multi-step business rules in the feature service.
- Include the router from `main.py` and give routes useful tags for `/docs`.

### `service.py`

- Own feature business rules and SQLAlchemy operations.
- Accept the session and required user/resource identifiers explicitly.
- Scope every resource read and write to the authenticated owner.
- Keep HTTP types and request objects out of reusable domain logic.
- Use transactions where a multi-step change must be atomic, and surface
  expected not-found or conflict outcomes clearly to the router.

For example, the lesson service owns lesson and topic persistence; the lesson
router handles HTTP requests. Do not add all feature endpoints to one global
router or put all business logic in a single service.

## 4. Authentication and ownership

Authentication is implemented with FastAPI Users using bearer JWTs. Current
router prefixes include `/auth/jwt`, `/auth`, and `/users`; these are mounted by
`main.py`. Registration, login, password reset, and verification are
authentication operations, not lesson/project resource APIs.

`GET /users` lists active users for an authenticated caller. It returns only
`id` and `fullname` (not email, password/account flags, or other account
details), is sorted by full name and ID, and accepts `skip` and `limit`
pagination parameters (`limit` is capped at 100). The route and query live in
`users/router.py` and `users/service.py`; FastAPI Users continues to own the
authentication, current-user, and per-user management routes.

### Lesson endpoints

Implemented in `modules/lesson/router.py` and `modules/lesson/service.py`.
Both require an active authenticated user and are scoped to that user's own
lessons:

| Method and path            | Response                                                                                                           |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `GET /lessons`             | `list[LessonSummaryRead]` (no topics), newest first. Accepts `skip` (default 0) and `limit` (default 20, max 100). |
| `GET /lessons/{lesson_id}` | `LessonRead`: the lesson plus its topics ordered by `position`.                                                    |

A lesson that does not exist and a lesson owned by another user both return
`404 Lesson not found`. The `embedding` columns are never exposed. Lesson and
topic write endpoints (create, update, delete) are not implemented yet.

Lesson Mentor has one application user type: User. There is no admin role or
role-based permission hierarchy. For every private resource endpoint:

1. Require the active authenticated user.
2. Obtain the owner ID from that user, not from request input.
3. Filter resource queries and mutations by the owner ID.
4. For nested content, verify ownership through the parent lesson/project.
5. Return not-found behavior for inaccessible resources so one user cannot
   enumerate another user's data.

The frontend may hide actions for usability, but the backend remains
authoritative for ownership.

## 5. Models, schemas, and migrations

`models/models.py` currently contains the SQLAlchemy declarative base and User,
Lesson, and Topic models. `schemas.py` contains the user schemas used by
authentication. Keep ORM models focused on persistence; use Pydantic schemas
for API contracts and validation.

Lesson and Topic include an optional non-negative integer `time_frame`, in
minutes. The Alembic migration adds nullable columns so existing records remain
valid; database check constraints reject negative values. `schemas.py` now
holds the read schemas `TopicRead`, `LessonSummaryRead`, and `LessonRead`; there
are no lesson/topic request (create/update) schemas yet. The `Lesson.topics`
relationship is `lazy="raise"`, so the service loads topics explicitly with
`selectinload` where they are needed.

Alembic revision files live in `alembic/versions/`. Database initialization
(engine/session setup and applying schema revisions) is distinct from seeding
records.

Alembic uses the normalized `database_url` from `config/db.py`. Apply the
current revisions with `uv run alembic upgrade head` from `backend/`.

## 6. Database seeding

`backend/seed.py` uses Faker to add two stable demo users, two lessons per user,
and three topics per lesson. The operation is explicit and repeatable: it
reuses the fixed `@example.com` users and adds only missing seed lessons.
Both accounts use the shared password `password`; rerunning the script resets
these seed users to that password. This weak password is for local development
only, never production. Names and lesson/topic descriptions are reproducible
through Faker's fixed seed. The script does not run during app startup and does
not create an admin.

Run from `backend/` after applying migrations:

```sh
uv run alembic upgrade head
uv run python seed.py
```

To fill time estimates on existing lesson/topic records only, without creating
or changing users, lessons, or topics, run `uv run python seed_time_frames.py`.
It fills only null values, uses 15–60 minutes per topic, and sets each missing
lesson estimate to the sum of its topic estimates.

## 7. AI generation and content management

AI-assisted generation is part of the target product, but no provider, model,
library, or AI integration is present in the backend dependencies or source.
Do not imply otherwise.

When generation is implemented, isolate orchestration in the
`ai_generation` feature service/router. The generation agent's responsibility
is to turn a user's request and validated options into structured draft
lesson/project content; it must not decide resource access or independently
persist user-owned records. Validate the draft, then hand it to the ordinary
lesson or project service for ownership-aware persistence. Manual creation and
AI-generated content should be managed through the same resource services, so
users can review, edit, and delete their own content without AI-specific CRUD
behavior.

Do not choose a vendor, model, or prompt framework in documentation until the
project establishes one.

## 8. Commands and maintenance

Available package metadata and versions are in `pyproject.toml` and `uv.lock`.
Use `uv sync` so the declared Faker dependency is installed. From `backend/`:

```sh
uv sync
uv run fastapi dev main.py
```

There is currently no backend test command or configured test suite. The
database is expected to be migrated before seeding.
