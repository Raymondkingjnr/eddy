# Lesson Mentor backend

The backend is a Python FastAPI application. It currently provides FastAPI
Users JWT authentication, SQLAlchemy User, Lesson, and Topic models, and
read-only lesson endpoints. Lesson write endpoints (create, update, delete),
project endpoints, and AI generation are not implemented yet.

## Requirements and local setup

Python `>=3.11,<3.14` is specified in `pyproject.toml`. The project has a `uv`
lockfile and a `requirements.txt`. Run from `backend/`:

```sh
uv sync
```

Configure `DATABASE_URL` for PostgreSQL and a strong `JWT_SECRET` in the local
environment (or a local `.env` file). Do not commit `.env` files or secrets.
For direct cross-origin frontend requests, set `FRONTEND_URL` to the allowed
frontend origin (or a comma-separated list of origins). The Vite development
proxy avoids cross-origin requests during local development.
Then run the development API:

```sh
uv run fastapi dev main.py
```

FastAPI's interactive API documentation is available at `/docs`.

## Current structure

```text
backend/
  main.py
  config/
  models/models.py
  schemas.py
  users/users.py
  api/lesson/
    router.py
    service.py
  alembic/
```

The `main.py` module mounts the current authentication, user, and lesson
routers. Database models are in `models/models.py`; authentication and lesson
schemas are in `schemas.py`.

An authenticated `GET /users` directory endpoint returns active users' IDs and
full names with `skip`/`limit` pagination. It intentionally excludes account
emails and authentication fields. The endpoint delegates to `users/service.py`.

Authenticated lesson endpoints (own lessons only):

- `GET /lessons` lists lessons, newest first, with `skip`/`limit` pagination
  (`limit` max 100). Topics are not included.
- `GET /lessons/{lesson_id}` returns one lesson with its topics ordered by
  `position`. A missing lesson and another user's lesson both return 404.

New features should have their own router and service, following
`modules/lesson/router.py` and `modules/lesson/service.py`. Routers own HTTP
validation, dependency injection, and responses. Services own domain rules and
database operations. Keep AI generation orchestration separate from normal
lesson/project CRUD and pass generated drafts through the same ownership-aware
resource services used by manual creation.

## Authentication, ownership, and roles

There is one application user type: User. Do not add an admin role, dashboard,
or role-based permission tiers. Protected resource routes must use the active
authenticated user and query only resources owned by that user. Never accept a
resource owner's ID as authority from request data.

## Migrations and seeding

Alembic revisions live in `alembic/versions/`. Keep schema migration and data
seeding separate. After setting the local `DATABASE_URL`, apply the current
schema and seed two demo users with two lessons and three topics per lesson:

```sh
uv run alembic upgrade head
uv run python seed.py
```

The development seed is safe to rerun: it reuses the two fixed `@example.com`
accounts and adds only missing seed lessons. Both demo users use the password
`password`; rerunning the script resets those two seed accounts to that
password. This intentionally weak, shared password is for local development
only and must not be used in production. Faker-generated names and lesson text
are deterministic. Seeding runs only when invoked; application startup does not
create or populate records.

To add estimated minutes to existing lessons and topics without creating or
changing users/lessons/topics, run:

```sh
uv run alembic upgrade head
uv run python seed_time_frames.py
```

The time-frame seed only fills unset values. Topic estimates are 15–60 minutes;
each lesson estimate is set to the sum of its topic estimates.

See [backend-fastapi.md](../backend-fastapi.md) for backend architecture,
ownership, and AI-generation conventions, and [testing.md](../testing.md) for
the current testing status.
