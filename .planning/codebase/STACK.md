# Technology Stack

**Analysis Date:** 2026-06-21

## Languages

**Primary:**
- **TypeScript** ~5.8.2 — All application source code (`server.ts`, `src/`, `vite.config.ts`). Targets ES2022. Uses React JSX (`react-jsx` transform).
- **CSS** — Tailwind CSS v4 directives in `src/index.css`. Custom Google Fonts import (Inter, JetBrains Mono).

**Secondary:**
- **HTML** — `index.html` entry point as Vite SPA shell.
- **JSON** — Configuration files (`firebase-applet-config.json`, `firebase-blueprint.json`, `metadata.json`, `tsconfig.json`).

## Runtime

**Environment:**
- **Node.js** 20+ (inferred from tsconfig `target: ES2022`, `@types/node ^22.14.0`, and `moduleResolution: "bundler"`). Run via `tsx` for development (`npm run dev` uses `tsx server.ts`), compiled via `esbuild` for production (`npm run build`).

**Package Manager:**
- **npm** — Lockfile: `package-lock.json` (present). No `yarn.lock` or `pnpm-lock.yaml`.
- Scripts defined in `package.json`:
  - `dev`: `tsx server.ts` — Development server with HMR
  - `build`: `vite build && esbuild server.ts --bundle --platform=node --format=cjs --packages=external --sourcemap --outfile=dist/server.cjs` — Production bundle
  - `start`: `node dist/server.cjs` — Production start
  - `clean`: `rm -rf dist`
  - `lint`: `tsc --noEmit`

## Frameworks

**Core:**
- **Express** `^4.21.2` — HTTP server, serves REST API (`server.ts`). Routes: `/api/health`, `/api/webhook/whatsapp`, `/api/orders/:id`, `/api/simulate`, `/api/flows`, `/api/flows POST`. Also serves Vite dev middleware or static dist in production.
- **React** `^19.0.1` — UI framework (`react`, `react-dom`). Client-side SPA via `src/main.tsx` mounting to `#root` in `index.html`. Uses StrictMode.
- **Vite** `^6.2.3` — Build tool and dev server middleware. Plugins: `@vitejs/plugin-react`, `@tailwindcss/vite`.
- **Firebase Client SDK** `^12.15.0` — Firestore, Auth, initialized from `firebase-applet-config.json`. Used both client-side (`src/lib/firebase-client.ts`) and server-side (`server.ts`).
- **Firebase Admin SDK** `^14.0.0` — Listed in dependencies, imported but not actively used in current server code.
- **@google/genai** `^2.4.0` — Google Generative AI SDK for Gemini API calls in `src/lib/gemini.ts`.

**Testing:**
- **Not detected** — No test files, no Jest/Vitest config, no test scripts in `package.json`.

**Build/Dev:**
- **Vite** `^6.2.3` — Frontend bundler with HMR. Config at `vite.config.ts`. Alias `@` → root directory.
- **esbuild** `^0.25.0` — Server bundler for production (`esbuild server.ts --bundle ...`).
- **tsx** `^4.21.0` — TypeScript execution engine for development (`npm run dev`).
- **TypeScript** `~5.8.2` — Type checking (`tsc --noEmit`). Config at `tsconfig.json`.
- **Tailwind CSS** `^4.1.14` — Utility-first CSS framework via `@tailwindcss/vite` plugin.
- **Autoprefixer** `^10.4.21` — Listed in devDependencies but not explicitly configured (PostCSS config not found).

## Key Dependencies

**Critical:**
| Package | Version | Purpose | Where Used |
|---------|---------|---------|------------|
| `express` | ^4.21.2 | REST API server | `server.ts` |
| `react` / `react-dom` | ^19.0.1 | Component UI framework | `src/App.tsx`, all components |
| `@google/genai` | ^2.4.0 | Gemini LLM API client | `src/lib/gemini.ts` |
| `firebase` | ^12.15.0 | Firebase Client SDK (Firestore, Auth) | `server.ts`, `src/lib/firebase-client.ts`, all view components |
| `firebase-admin` | ^14.0.0 | Firebase Admin SDK (server-side/admin operations) | `package.json` (listed but import not active in current code) |
| `vite` | ^6.2.3 | Build tool, HMR dev server middleware | `vite.config.ts`, `server.ts` |
| `dotenv` | ^17.2.3 | Load `.env` files for `GEMINI_API_KEY` | `server.ts` (imported indirectly) |
| `tailwindcss` | ^4.1.14 | Utility CSS framework | `src/index.css` via `@tailwindcss/vite` |
| `yaml` | ^2.9.0 | YAML parsing for workflow DSL | `package.json` (listed) |

**UI & Utility:**
| Package | Version | Purpose |
|---------|---------|---------|
| `lucide-react` | ^0.546.0 | SVG icon library (used extensively in all components) |
| `motion` | ^12.23.24 | Animation library (Framer Motion v12, imported as `motion/react`) |
| `clsx` | ^2.1.1 | Conditional CSS class utility |
| `tailwind-merge` | ^3.6.0 | Merge Tailwind classes without conflicts |
| `date-fns` | ^4.4.0 | Date manipulation (listed but not imported in current source) |

**Dev Dependencies:**
| Package | Version | Purpose |
|---------|---------|---------|
| `typescript` | ~5.8.2 | Type checking and compilation |
| `tsx` | ^4.21.0 | TypeScript execution for dev |
| `esbuild` | ^0.25.0 | Server bundling for production |
| `@types/express` | ^4.17.21 | TypeScript types for Express |
| `@types/node` | ^22.14.0 | TypeScript types for Node.js |
| `autoprefixer` | ^10.4.21 | CSS vendor prefixing |
| `tailwindcss` | ^4.1.14 | CSS framework |
| `vite` | ^6.2.3 | Build tool |

## Configuration

**TypeScript (`tsconfig.json`):**
- `target`: ES2022
- `module`: ESNext with `moduleResolution: "bundler"`
- `jsx`: `react-jsx` (automatic JSX transform)
- `paths`: `@/*` → `./*` (path alias)
- `experimentalDecorators`: true
- `strict`: not explicitly set (inferred as off)
- `allowImportingTsExtensions`: true
- `noEmit`: true (Vite/esbuild handle compilation)

**Vite (`vite.config.ts`):**
- Plugins: `react()`, `tailwindcss()`
- Alias: `@` → project root
- HMR: configurable via `DISABLE_HMR` env var (disabled in AI Studio)
- File watching: disabled when `DISABLE_HMR=true` (agent-friendly)

**Environment:**
- Two env vars required (from `.env.example`):
  - `GEMINI_API_KEY` — API key for Gemini AI
  - `APP_URL` — Self-referencing URL for the applet (Cloud Run service URL)
- Loaded via `dotenv` package (in development via `tsx`)
- `.env*` files in `.gitignore` (only `.env.example` tracked)

**Firebase Configuration:**
- `firebase-applet-config.json` — Firebase project credentials (projectId, apiKey, authDomain, firestoreDatabaseId, storageBucket)
- `firebase-blueprint.json` — Data model schema (Order, Simulation, Invoice, Flow, ParserAudit entities)
- `firestore.rules` — Firestore security rules (currently wide-open: `allow read, write: if true`)
- `metadata.json` — App metadata (name: "CCAM", description, capabilities)

## Platform Requirements

**Development:**
- Node.js 20+
- npm
- Gemini API key (`GEMINI_API_KEY` env var)
- Firebase project (Firestore database must exist)

**Production:**
- Google Cloud Run (AI Studio deployment target, `APP_URL` env var injected at runtime)
- Firebase Firestore database (named `ai-studio-0c226e45-1671-429f-a15d-f7b5db246e6b`)
- Gemini API key configured as user secret in AI Studio

## Architecture Notes

- **Monorepo structure** — Single `package.json` serves both frontend (Vite SPA) and backend (Express server). No workspaces or monorepo tooling.
- **Not a true Next.js project** — Despite being described as Next.js in project context, the actual implementation uses Express for SSR/API + Vite SPA for frontend. No `next.config.js`, no `pages/` or `app/` directory.
- **No testing framework** — Zero test files, no test runner configuration, no coverage tooling.
- **No Docker configuration** — Dockerfile not found. SystemsView UI references Docker/K8s but no actual configs exist in the repo.
- **No CI/CD files** — No `.github/`, `.gitlab-ci.yml`, or other CI configs found.
- **No linter configuration** — No `.eslintrc`, `biome.json`, or other linting configs. Only `tsc --noEmit` for static checking.

---

*Stack analysis: 2026-06-21*
