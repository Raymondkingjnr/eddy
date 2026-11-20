# Lesson Mentor frontend

The frontend is a Vue 3 and TypeScript single-page application built with Vite,
Vue Router, and Tailwind CSS. It is currently a prototype: its landing and
dashboard views still include course/booking demo content. Login, registration,
and protected dashboard access are connected to the FastAPI backend.

## Requirements

- Node.js `^22.18.0 || >=24.12.0` (see `package.json`)
- pnpm

## Start developing

Run these commands from `frontend/`:

```sh
pnpm install
pnpm dev
```

The Vite development server prints its local URL when it starts.

## Available scripts

```sh
pnpm run type-check
pnpm test
pnpm run build
pnpm run preview
```

- `type-check` checks Vue and TypeScript types.
- `test` runs Vitest tests from `test/`.
- `build` runs type-checking and creates the production build.
- `preview` serves a previously built application.
  course/booking screens. It is not the FastAPI backend.

The `lint` and `format` scripts include autofix/write options. Review their
effects before running them.

## Backend authentication

The login and registration forms use the FastAPI Users endpoints through the
shared frontend API client. During local development Vite proxies `/api` to
`http://127.0.0.1:8000`; start the backend separately. Set
`VITE_API_BASE_URL` to the backend origin when the frontend should call a
deployed API directly. In that case configure the backend's `FRONTEND_URL` to
allow the frontend origin.

The access token is kept in `sessionStorage` and sent as a bearer token by the
API client. The dashboard is protected by the router guard. Pages and
components call auth service/composable methods and do not construct API URLs.

See [frontend-vue.md](../frontend-vue.md) for component, API, styling-token, and
accessibility conventions.
