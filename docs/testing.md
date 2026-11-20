# Testing guidance

This repository is an early prototype. Its frontend package includes Vitest,
with focused tests for the auth service and API client. No component-test
utilities are present. The backend has no configured test framework, test
dependencies, or test suite. Do not describe unconfigured tests or
continuous-integration jobs as existing.

## What to test as features are added

| Change | Useful coverage |
| --- | --- |
| FastAPI endpoint | Request validation, response shape/status, authentication, and ownership |
| Lesson/project service | Persistence, domain rules, and user scoping |
| AI generation workflow | Valid draft shape, validation failures, persistence ownership, and surfaced provider failures once a provider is selected |
| Frontend API service | Exact URL, method, request body, response mapping, and error behavior |
| Vue component with behavior | User-visible text, accessible controls, emitted events, loading and error states |
| Bug fix | A regression case that fails without the fix |
| Database migration | Upgrade/downgrade behavior and compatibility with the configured database |

There is one application user type, not a set of permission roles. For protected
resources, test that the owner can access their lesson/project and that a
different authenticated user cannot read, edit, or delete it. Also cover
unauthenticated requests.

## Frontend test conventions

Vitest is available through the existing `test` script. Put every frontend test
file in `frontend/test/`, separate from application source. Auth service and API
client tests live there. Keep tests deterministic:

- Do not depend on real network requests, wall-clock timing, or test order.
- Use fake API responses and assert request details and visible outcomes.
- Prefer accessible labels, roles, and user-visible text over CSS class or
  implementation details.
- Test async loading, empty, and error paths when they are part of the feature.

No component testing utility or DOM environment is currently declared in
`frontend/package.json`. Before adding mount-based component tests, add and
configure the required dependency in a separately reviewed dependency change.

## Backend test conventions

The backend has no test runner configured. Select and add a Python test
framework/dependencies before publishing a backend test command. Once a runner
exists, keep tests isolated from external services and use a test database
configuration that matches the actual SQLAlchemy models and migrations.

## Existing validation commands

Run frontend commands from `frontend/`:

```sh
pnpm run type-check
pnpm test
pnpm run build
```

`pnpm test` runs `vitest run`.
`pnpm run build` performs type-checking and the Vite production build. The
configured `lint` and `format` scripts use autofix/write flags, so review their
effects before using them as checks.

There is no backend test command. Alembic migration execution is also not
verified: `alembic/env.py` imports a `DATABASE_URL` name that is not defined in
`config/db.py`. Do not claim migration validation until that mismatch is
resolved.

## Test integrity

- Keep failures visible; fix the cause rather than deleting or weakening a test.
- Avoid snapshots unless serialized output itself is the requirement.
- Never log passwords, tokens, or other credentials from test fixtures.
- Do not test Vue, FastAPI, or third-party library behavior; test Lesson Mentor
  behavior and contracts.
