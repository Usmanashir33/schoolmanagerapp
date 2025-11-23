## Purpose

This repository is a React + Vite frontend using Tailwind CSS and several custom React Contexts and Hooks. The goal of this file is to give AI coding agents immediately useful, project-specific guidance so they can make safe, consistent edits.

## Big picture (how the app is organized)

- Vite + React (SWC) app at the project root. Dev server: Vite (host 0.0.0.0, port 5173).
- UI is component-based under `src/components/` (PascalCase filenames, many `.jsx`).
- App-wide state and cross-cutting utilities live in:
  - `src/customContexts/` — React Context providers (e.g. `AuthContext.jsx`, `UiContext.jsx`, `LiveContext.jsx`, `StaffContext.jsx`).
  - `src/customHooks/` — custom hooks for requests and app logic (e.g. `RequestHook.jsx`, `ExternalRequestHook.jsx`, `WebSocketHook.jsx`, `ConfigDetails.jsx`).
- Special admin area is under `src/components/AAStaff/` (admin components and pages).

## Key conventions and patterns (explicit, discoverable)

- Auth & tokens:
  - Tokens are stored in `localStorage` under `a_token` (access) and `r_token` (refresh).
  - `src/customContexts/AuthContext.jsx` exposes `getToken()`, `refreshToken()`, `isAuthenticated`, and `logout` — prefer using these helpers when interacting with authenticated endpoints.

- Network requests:
  - `src/customHooks/RequestHook.jsx` is the canonical pattern. It uses an `AbortController`, reads token via `getToken()`, sets UI state (`setIsLoading`, `setError`) from `UiContext`, and exposes `sendRequest(url, method, formdata, withLoading)` and `sendArbitRequest(...)`.
  - `RequestHook` processes named responses via `processResponseData` (e.g., response objects with `name: 'transections'` or `name: 'notifications'`) — when adding new API handlers, follow this pattern.

- UI loading/error flow:
  - Most hooks/components call `setIsLoading(true)` before requests and clear it after; errors are reported via `setError` in `UiContext`.

- File naming and types:
  - Components are PascalCase `.jsx` files in `src/components/` (some files are `.tsx` where TypeScript was used, e.g. `Financial-Dashboard-Layout.tsx`).
  - Tailwind content scanning includes `./src/**/*.{html,js,jsx,ts,tsx}` (see `tailwind.config.js`).

- Routing and versions:
  - The project uses `react-router` / `react-router-dom` (v7.x in package.json). Expect route components under `src/components/` (e.g., `MainDashbord.jsx`, `Home.jsx`).

- ESLint specifics:
  - ESLint config is in `eslint.config.js`. Note rule: `'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }]` — variables starting with uppercase or underscore are ignored (common for React components/constants).

## Build / run / lint (concrete commands)

- Install dependencies:
  - npm install
- Start dev server (HMR):
  - npm run dev
  - Dev server uses Vite (host 0.0.0.0, port 5173 by default — see `vite.config.js`).
- Build for production:
  - npm run build
- Preview production build locally:
  - npm run preview
- Lint:
  - npm run lint

## Integration points & external dependencies to be careful with

- WebSockets: There are `WebSocketHook.jsx` files (root `src/` and `src/customHooks/`) — check which one is imported where before editing.
- API base URL is defined in `src/customHooks/ConfigDetails.jsx` — change that to point to different backends.
- Third-party libs in use: `echarts`, `jwt-decode`, FontAwesome, `react-icons`, `heic2any`. When upgrading, verify bundle size and SWC compatibility.

## How to make safe changes (short checklist)

1. Search usages before renaming: many components/hooks are referenced by plain imports (no index barrel files). Use global search for the symbol.
2. When altering request flows, update `RequestHook.jsx`’s `processResponseData` or add corresponding handlers so UI state updates stay consistent.
3. Preserve token handling: use `authContext.getToken()` and `authContext.isAuthenticated` instead of directly reading `localStorage` in new code.
4. Match UI feedback: set `setIsLoading(true)` / `setIsLoading(false)` and call `setError(...)` consistently.
5. Respect ESLint rules and the `no-unused-vars` naming pattern when introducing temporary names.

## Where to look for examples

- Auth and token lifecycle: `src/customContexts/AuthContext.jsx` (refresh flow + `getToken`).
- Canonical request patterns: `src/customHooks/RequestHook.jsx` (sendRequest / sendArbitRequest, AbortController pattern).
- UI state usage: `src/customContexts/UiContext.jsx` and components that call `setIsLoading`/`setError`.

## Notes for AI agents merging with existing guidance

- No existing `.github/copilot-instructions.md` was discovered; this file is newly created. If you find human-written guidance later (AGENT.md/AGENTS.md), prefer the human guidance for policy/priority decisions and merge concrete commands/examples into this file.

---
If anything important is missing or inaccurate (external API base, test commands, or CI steps), tell me which areas to expand and I will update this file.
