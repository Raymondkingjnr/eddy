# Frontend guide: Vue 3, TypeScript, and Tailwind CSS

This guide describes the existing Vue/Vite prototype and conventions for
connecting it to the Lesson Mentor API. It does not describe a server-rendered
framework or claim that the API integration already exists.

## 1. Current stack and layout

- Vue 3 Single File Components and TypeScript
- Vite and Vue Router
- Tailwind CSS 4 through `@tailwindcss/vite`
- Vitest runner
- `pnpm` lockfile; Node.js engine `^22.18.0 || >=24.12.0`

Current application structure:

```text
frontend/
  src/
    App.vue
    main.ts
    routers/index.ts
    views/
      landing-page.vue
      login.vue
      register.vue
      dashboard.vue
    components/
    assets/main.css
    data.ts
  db.json
  package.json
  vite.config.ts
```

There are no framework-style `pages/` or layouts. Auth services and a shared API
client now live under `src/services/`, and auth state is exposed by
`src/composables/useAuth.ts`. The landing page's course and booking demo code
uses a separate catalog service; `db.json` and the `server` script remain local
prototype fixtures, not the Lesson Mentor backend.

## 2. Setup and scripts

From `frontend/`:

```sh
pnpm install
pnpm dev
```

Useful package scripts:

```sh
pnpm run type-check
pnpm test
pnpm run build
pnpm run preview
pnpm run server
```

`pnpm run build` runs type-checking and the production build. `pnpm run server`
starts the local JSON Server fixture on port 3001. It is for the current demo
only; do not describe it as the FastAPI service.

The configured `lint` and `format` scripts include write/fix flags. Review their
effects before running them; they are not read-only verification commands.

## 3. Components, views, and routing

- Keep route records in `src/routers/index.ts`.
- Use `src/views/` for route-level screens and `src/components/` for reusable
  interface elements.
- Use `<script setup lang="ts">` for Vue components and declare prop and event
  types where practical.
- Keep one component focused on one visual or interaction responsibility.
- Give repeated lists stable keys and use semantic elements and accessible
  labels for controls.
- Keep navigation and route behavior in Vue Router; do not introduce framework
  conventions that are absent from this Vite application.

The login and registration screens call the FastAPI authentication service
through the shared API client. The dashboard route requires an authenticated
user. During local development Vite proxies `/api` to FastAPI on port 8000.
For direct cross-origin API calls, configure the backend `FRONTEND_URL` and
frontend `VITE_API_BASE_URL`. Lesson/project APIs and AI generation are not yet
integrated.

## 4. API and domain code

The auth workflow is connected to the backend. When wiring lesson/project
features:

- Add small typed API/service modules under `src/` (for example,
  `src/services/lessonService.ts`) to own endpoint URLs, HTTP methods, request
  bodies, and response mapping.
- Keep view components focused on presentation, form state, and user feedback;
  avoid duplicating request logic across components.
- Define request/response types near their domain and keep them aligned with
  FastAPI Pydantic schemas.
- Keep all API paths and HTTP calls in services/API client modules. Never call
  `fetch` or construct backend endpoints in a view or component.
- Send authentication credentials through one shared API client once the
  frontend authentication flow is implemented. Do not store or log secrets.
- Treat frontend access checks as presentation only. The backend must enforce
  resource ownership.

Manual lesson/project creation and AI-assisted generation should result in the
same resource shapes and use the same edit/manage UI. Generation-specific
request state belongs in a separate workflow from ordinary lesson CRUD.

## 5. Tailwind and CSS custom properties

Tailwind is the active styling approach. `src/assets/main.css` currently imports
Tailwind and defines a Plus Jakarta Sans font theme; it does not yet contain a
semantic `:root` token system.

Continue using Tailwind utilities for layout, responsive behavior, and
component structure. For shared design values that should survive a later move
to plain CSS:

1. Define semantic custom properties in `:root` in `src/assets/main.css`.
2. Reuse tokens for the current indigo accent, neutral backgrounds/text,
   borders, radii, and typography. Confirm the concrete values against the
   existing visual design before centralizing them.
3. Use a small shared spacing scale (for example `--space-1`, `--space-2`)
   only for repeated design values; keep one-off layout on Tailwind spacing
   utilities.
4. Reference tokens from CSS with `var(--token-name)` or from Tailwind
   arbitrary-value utilities such as `bg-[var(--color-primary)]`.
5. Prefer semantic names (`--color-primary`, `--color-surface`,
   `--color-foreground`, `--color-border`, `--radius-md`) over palette-specific
   names in component styles.
6. Keep utility classes for one-off layout; do not hardcode a new color or
   radius in several components when it should be a shared token.

For a starting token map, the existing styles use indigo accent colors,
neutral/white surfaces, gray text/borders, and Tailwind's rounded utilities:

```css
:root {
  --color-primary: var(--color-indigo-600);
  --color-primary-hover: var(--color-indigo-700);
  --color-background: var(--color-neutral-50);
  --color-surface: var(--color-white);
  --color-foreground: var(--color-gray-900);
  --color-muted: var(--color-gray-500);
  --color-border: var(--color-gray-200);

  --radius-small: var(--radius-lg);
  --radius-medium: var(--radius-xl);
  --radius-large: var(--radius-2xl);

  --space-1: calc(var(--spacing) * 1);
  --space-2: calc(var(--spacing) * 2);
  --space-3: calc(var(--spacing) * 3);
  --space-4: calc(var(--spacing) * 4);
}
```

These aliases use the current Tailwind palette/scale as a migration aid. Check
their rendered values against the interface before treating them as stable
design tokens; the aliases are guidance and are not present in the stylesheet
yet.

Avoid converting all existing utility classes as part of unrelated work. New
styles should make gradual migration to plain CSS possible without introducing
a second competing design system.

## 6. Errors, accessibility, and async behavior

- Show loading, empty, and error states for asynchronous screens.
- Do not ignore failed requests or report success after an unsuccessful
  operation.
- Use the `vue-sonner` toaster mounted once in `src/App.vue` for transient
  success, error, and informational messages. Trigger notifications through
  `src/services/notifications.ts`; use `notifyRequestError` for server/client
  request failures so safe 4xx details can be shown and server failures use a
  friendly fallback. Do not duplicate the same failure in an inline alert and
  a toast.
- Toast success or info messages only after the operation has completed or when
  the user needs immediate client-side feedback. Never present an unsuccessful
  request as successful.
- Use labels, keyboard-operable controls, visible focus, and appropriate
  semantic markup.
- Announce meaningful status changes and do not use color as the only status
  signal.
- Disable duplicate submissions while a request is pending where appropriate.
- Cancel or ignore stale requests when changing routes or search inputs if an
  older response could overwrite newer state.

## 7. Current validation

`frontend/package.json` defines `type-check`, `test`, and `build` scripts.
Keep all Vitest files in `frontend/test/`, outside `src/`. Tests cover the auth
service and API client. No component-test utility or DOM environment is
currently configured. See [testing.md](testing.md) for current limitations and
test expectations for future features.
