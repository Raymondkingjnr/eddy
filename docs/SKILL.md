---
name: eddy-engineering-standards
description: Project guidance for Lesson Mentor, a Vue 3 and TypeScript frontend with Tailwind CSS and a Python FastAPI backend. Use when changing, reviewing, testing, or documenting this project.
---

# Lesson Mentor engineering standards

These notes describe the current prototype and the conventions for growing it
into the Lesson Mentor product. Keep those two states distinct: a documented
target feature is not necessarily implemented.

## 1. Product and current status

Lesson Mentor is intended to help a user create and manage educational lessons
and projects. Users should be able to create content manually or request
AI-assisted lesson/project generation, edit lesson content, delete lessons,
and manage only their own resources.

The current repository is an early prototype:

- The frontend is a Vue 3, TypeScript, Vite, Vue Router, and Tailwind CSS app.
- Frontend registration, login, current-user lookup, logout, and the protected
  dashboard are connected to the FastAPI Users JWT authentication routes via
  `src/services/apiClient.ts` and `src/services/authService.ts`.
- The backend is a Python FastAPI app with FastAPI Users JWT authentication,
  SQLAlchemy models, and Alembic migrations.
- The database currently has User, Lesson, and Topic models. The backend
  exposes read-only lesson endpoints (`GET /lessons`, `GET /lessons/{id}`) in
  `backend/modules/lesson/`. There is no Project model, lesson write
  (create/update/delete) API, project API, or AI generation integration yet.
  `backend/seed.py` seeds development users, lessons, and topics explicitly.
- The frontend does not yet call the lesson endpoints, and AI generation is not
  integrated. The landing screen still contains course/booking demo content
  backed by JSON Server.

Do not describe target features as working until their implementation exists.
Do not select or imply an AI provider, model, or library without an explicit
project decision.

## 2. Current project layout

```text
backend/
  main.py                 FastAPI app and authentication routers
  config/                 Settings, database engine, URL normalization
  models/models.py        SQLAlchemy User, Lesson, and Topic models
  schemas.py              Pydantic/FastAPI Users schemas
  users/                  JWT setup, directory router/service
  api/lesson/         Read-only lesson router/service (GET list, GET one)
  seed.py                 Explicit Faker development seed
  seed_time_frames.py     Fills missing time estimates on existing content
  alembic/                Database migrations

frontend/
  src/
    App.vue
    main.ts
    routers/              Vue Router configuration
    views/                Landing, login, registration, dashboard
    components/           Reusable Vue components
    assets/main.css       Tailwind import and font theme
  test/                   Vitest test files, kept outside src/
  db.json                 JSON Server demo data

backend-fastapi.md
frontend-vue.md
testing.md
```

Keep shared backend configuration and database models in their existing
locations unless a focused implementation change establishes a better home.
Avoid documenting directories that do not exist as if they were already present.

## 3. Backend architecture and API

Use Python, FastAPI, Pydantic, SQLAlchemy, and the dependencies already declared
in `backend/pyproject.toml`. Keep HTTP concerns separate from domain operations:

- A feature `router.py` owns REST endpoints, request/response schemas,
  dependency injection, validation, HTTP status codes, and API documentation.
- A feature `service.py` owns business rules and database operations for that
  feature. Keep transactions and ownership checks close to the data operation.
- Keep shared models, schemas, configuration, and database setup organized and
  reusable. Do not put unrelated feature endpoints and business logic into
  `main.py`.
- Use FastAPI dependencies for the database session and authenticated user.
  Return clear HTTP errors; use Pydantic validation rather than duplicating
  request parsing.

The backend keeps user routes/services under `users/`; the lesson feature is
the first to follow the `backend/modules/` layout. As further features are
implemented, organize them by domain under `backend/modules/`, for example:

```text
backend/
  main.py
  config/
  models/
  schemas.py
  users/
  api/
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

This is a growth convention, not a description of current files. Include each
feature router from `main.py`; keep routers thin and services independent of
HTTP request/response objects where practical. Use REST resource nouns and
standard HTTP methods for lesson, topic, and project operations.

## 4. Authentication and resource ownership

There is one application user type: User. Do not add an admin dashboard, admin
role, role hierarchy, or role-based permission system.

The current authentication setup uses FastAPI Users with bearer JWTs. Protect
private endpoints with the authenticated active-user dependency. For every
lesson, topic, or project read or mutation:

- Derive the owner from the authenticated user, never from a client-supplied
  `user_id`.
- Scope database queries by that owner. Also scope nested resources (such as a
  topic under a lesson) through the owned parent.
- Do not reveal whether another user's resource exists; return the same
  not-found behavior used for inaccessible resources.
- Keep public registration/authentication endpoints separate from protected
  resource routes.

Authentication proves identity; ownership checks enforce access. Frontend
visibility checks are not a substitute for backend authorization.

## 5. Data and seeding

SQLAlchemy models describe persisted data and Pydantic schemas describe API
input/output. Make schema changes through Alembic migrations; do not rely on
application startup to create or populate a production database.

Database initialization (engine/session setup and schema migrations) is separate
from data seeding. `backend/seed.py` is an explicit Faker seed for development
users, lessons, and topics; run it deliberately after migrations. Keep future
seed scripts repeatable and out of application startup. Do not create an admin
account or mix seed operations into schema migrations.

## 6. AI generation boundary

AI-assisted lesson and project creation is a target capability; no AI provider
or generation integration is present yet. Keep generation separate from ordinary
lesson/project CRUD:

- The AI-generation feature accepts a user's learning goal and any validated
  generation options, and returns structured draft content. Its agent
  responsibility is content drafting, not authentication, authorization, or
  independent resource persistence.
- A lesson or project service validates and persists that result as a resource
  owned by the requesting user.
- Manual creation and generated drafts must enter the same resource-management
  path, so users can edit and manage either kind of content consistently.
- Keep AI-specific orchestration out of ordinary CRUD services. Do not add
  provider names, model assumptions, prompt libraries, or external dependencies
  until they are chosen and implemented.

## 7. Frontend and styling

Use the existing Vue 3 Single File Component, TypeScript, Vue Router, and Vite
setup. Keep route definitions in `src/routers/`, route-level views in
`src/views/`, and reusable interface pieces in `src/components/`. The current
frontend does not yet have a service/API layer; when connecting it to FastAPI,
put request logic in small typed API/service modules rather than duplicating
`fetch` calls across views and components.

Tailwind CSS is the current styling system. Continue using its utilities for
layout and component styling, but use semantic CSS custom properties for shared
design values so a future move to plain CSS does not require replacing
component-specific hard-coded values:

- Define design tokens in a `:root` block in `src/assets/main.css`.
- Reuse semantic color, border, radius, and typography tokens; align values
  with the existing indigo/neutral visual palette before replacing current
  utilities.
- Keep Tailwind's spacing utilities for one-off layout. If a spacing value is
  reused as a design rule, define it in the shared `--space-*` scale instead
  of repeating literal CSS values.
- Use Tailwind utilities that reference a token (for example
  `bg-[var(--color-primary)]`) or ordinary CSS declarations using `var(...)`.
- Keep one-off layout utilities in Tailwind. Do not create a token for every
  isolated margin or dimension, and do not claim a token exists until it is
  added to the stylesheet.
- Avoid introducing new hard-coded color values or radii when an existing token
  or Tailwind utility expresses the same design intent.

The current stylesheet imports Tailwind and defines a Plus Jakarta Sans font
theme; it does not yet define the semantic `:root` token set.

## 8. Code quality and errors

- Keep changes focused, typed, and consistent with nearby code.
- Prefer explicit TypeScript types and narrow `unknown`; avoid `any`.
- Give async UI states clear loading, empty, and error behavior. Do not silently
  swallow request failures.
- Use the app-level `vue-sonner` toaster from `App.vue` for transient success,
  error, and info messages. Call the shared notification helpers in
  `frontend/src/services/notifications.ts`; avoid duplicate inline-error and
  toast messages, and do not show unsafe server failures verbatim.
- Validate all client input on the server. Return appropriate 4xx responses and
  avoid exposing exception details or secrets to users.
- Do not commit credentials, `.env` contents, tokens, or real personal data.
- Keep user-facing text and visual status accessible; do not rely on color alone.

## 9. Development and testing

The frontend package scripts are defined in `frontend/package.json`; backend
dependencies and Python constraints are in `backend/pyproject.toml`. See
[frontend-vue.md](frontend-vue.md), [backend-fastapi.md](backend-fastapi.md),
and [testing.md](testing.md) for verified commands and current testing gaps.

The frontend has Vitest tests for its auth service and API client, but no
backend test framework or component-test utilities are configured. Add tests
alongside new behavior using the existing frontend runner; establish a backend
test runner before adding backend tests. Test both successful ownership access
and attempts to access another user's resources.
