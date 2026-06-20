# Codebase Structure

**Analysis Date:** 2026-06-21

## Directory Layout

```
ccam/
├── src/                          # React frontend SPA source
│   ├── components/               # UI view and overlay components (11 views + 3 shared)
│   │   ├── CommandPalette.tsx     # ⌘K command palette overlay
│   │   ├── ComplianceView.tsx     # Governance roadmap, PDPA, encryption, audit trail
│   │   ├── DashboardView.tsx      # KPI cards, charts, financial ROI
│   │   ├── FinancialsView.tsx     # Payment funnel, invoice engine, settlement buffer
│   │   ├── FlowsView.tsx          # YAML workflow DSL editor + active deployment registry
│   │   ├── GovernanceView.tsx     # Onboarding, HITL pipeline, SLO/SLA, SRE playbooks
│   │   ├── HitlModal.tsx          # Human-in-the-Loop correction modal overlay
│   │   ├── OnboardingWizard.tsx   # Multi-step tenant provisioning (IDENTITY→SCHEMA→FLOW→COMPLETE)
│   │   ├── OrdersView.tsx         # Live order buffer with Firestore onSnapshot
│   │   ├── QAView.tsx             # Sign-off matrix, immutable audit trail viewer
│   │   ├── ReportsView.tsx        # Pilot KPI tracking, baseline analysis
│   │   ├── SettingsView.tsx       # Security matrix, data init, webhook config
│   │   ├── SimulatorView.tsx      # Digital twin configuration and run
│   │   └── SystemsView.tsx        # Topology, ERD, scaling, CI/CD, API spec, threat model
│   ├── lib/
│   │   ├── firebase-client.ts     # Firebase app init (Firestore + Auth)
│   │   └── gemini.ts              # Gemini 1.5 Flash WhatsApp message parser
│   ├── App.tsx                    # Root app shell: sidebar, tab routing, overlays
│   ├── index.css                  # Tailwind v4 imports, Inter + JetBrains Mono fonts
│   ├── main.tsx                   # React DOM mount point
│   ├── types.ts                   # TypeScript interfaces (Order, Invoice, ParserAudit, etc.)
│   └── utils.ts                   # cn() classname helper + FirestoreErrorHandler
├── .env.example                   # Required environment variables (GEMINI_API_KEY, APP_URL)
├── .gitignore                     # node_modules, build, dist, coverage, .env*
├── README.md                      # Local development instructions
├── firebase-applet-config.json    # Firebase project configuration (projectId, apiKey, etc.)
├── firebase-blueprint.json        # Data schema blueprint (Order, Simulation, Invoice, Flow, ParserAudit)
├── firestore.rules                # Firestore security rules (currently permissive)
├── index.html                     # Vite HTML entry point
├── metadata.json                  # AI Studio app metadata
├── package.json                   # Dependencies and scripts
├── package-lock.json              # Lockfile
├── seed.ts                        # CLI script to populate demo data (orders + flows)
├── server.ts                      # Express API server (health, webhook, orders, simulate, flows)
├── tsconfig.json                  # TypeScript config (ES2022, ESNext modules, bundler resolution)
└── vite.config.ts                 # Vite config (React plugin, Tailwind CSS plugin, path alias)
```

## Directory Purposes

### `src/` — Frontend Application Source
- **Purpose:** All React SPA source code — components, libraries, types, styles
- **Contains:** `.tsx` components, `.ts` libraries, `.css` stylesheets
- **Key files:**
  - `src/App.tsx`: Root component with sidebar navigation, tab routing, notification system, HITL modal, command palette
  - `src/main.tsx`: React entry point — `createRoot(document.getElementById('root')!).render(<App />)`
  - `src/types.ts`: All TypeScript interfaces — `Order`, `Invoice`, `ParserAudit`, `InventoryItem`, `SimulationConfig`, `SimulationResult`, `FlowDefinition`, `PilotMetrics`, `Report`
  - `src/utils.ts`: `cn()` function (clsx + tailwind-merge) and `handleFirestoreError()` utility

### `src/components/` — UI Components
- **Purpose:** All view components and shared overlay components
- **Contains:** 11 view screens + 3 shared components (CommandPalette, HitlModal, OnboardingWizard)
- **Naming:** PascalCase, `*View.tsx` for main screens, other names for overlays/wizards
- **State access:** Components use either Firestore `onSnapshot` (OrdersView, FinancialsView) or `fetch` API calls (SimulatorView, FlowsView)

### `src/lib/` — Library Modules
- **Purpose:** Non-component JavaScript/TypeScript modules
- **Contains:** Firebase client initialization, Gemini AI client wrapper
- **Key files:**
  - `src/lib/firebase-client.ts`: Initializes Firebase app with Firestore (long polling) and Auth. Singleton `db` and `auth` exports.
  - `src/lib/gemini.ts`: Single exported function `parseWhatsAppMessage(message)` that calls Gemini 1.5 Flash for structured order extraction.

### Root Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Project metadata, scripts (`dev`, `build`, `start`, `clean`, `lint`), dependencies |
| `tsconfig.json` | TypeScript compiler options (ES2022 target, ESNext modules, bundler resolution, React JSX) |
| `vite.config.ts` | Vite build config (React plugin, Tailwind CSS plugin, `@/` path alias, HMR/watching settings) |
| `firebase-applet-config.json` | Firebase project credentials (projectId, apiKey, authDomain, firestoreDatabaseId, storageBucket) |
| `firebase-blueprint.json` | Data schema design document defining 5 entity types and 6 Firestore collections |
| `firestore.rules` | Firestore security rules (currently `allow read, write: if true` for all documents) |
| `.env.example` | Template for required environment variables (GEMINI_API_KEY, APP_URL) |
| `index.html` | Vite HTML entry — `<div id="root">` and `<script src="/src/main.tsx">` |
| `metadata.json` | AI Studio app metadata (name, description, capabilities) |

### Root Server/Script Files

| File | Purpose |
|------|---------|
| `server.ts` | Express server with 6 REST endpoints + Vite middleware (dev) or static serve (prod). Entry for `npm run dev` and `npm run start`. |
| `seed.ts` | CLI data seeding script. Run with `tsx seed.ts`. Creates 2 demo orders and 1 demo flow in Firestore. |

## Module Organization

The codebase uses a flat, component-centric organization (no `api/`, `pages/`, `hooks/`, or `context/` directories):

```
src/
├── App.tsx              # Orchestrator — routing, overlays, global state
├── main.tsx             # React DOM mount
├── index.css            # Global styles + Tailwind
├── types.ts             # All TS interfaces (shared between components)
├── utils.ts             # Utility functions (cn, error handler)
├── lib/                 # External service clients
│   ├── firebase-client.ts
│   └── gemini.ts
└── components/          # All UI components
    ├── DashboardView.tsx
    ├── OrdersView.tsx
    ├── SimulatorView.tsx
    ├── FinancialsView.tsx
    ├── FlowsView.tsx
    ├── ComplianceView.tsx
    ├── GovernanceView.tsx
    ├── SystemsView.tsx
    ├── ReportsView.tsx
    ├── SettingsView.tsx
    ├── QAView.tsx
    ├── HitlModal.tsx
    ├── CommandPalette.tsx
    └── OnboardingWizard.tsx
```

**Notable absences:**
- No `api/` or `server/` directory — the Express server is a single `server.ts` at root
- No `pages/` directory — all views are components, not Next.js-style pages
- No `hooks/` directory — all hooks are inline within components
- No `context/` directory — no React Context used
- No `constants/` directory — constants defined inline in components
- No `assets/` directory in `src/` — only an `assets/` folder at root

## Server Route Organization

All API routes live in a single file (`server.ts`) with no routing subdirectory:

| Route | Method | Handler | Lines |
|-------|--------|---------|-------|
| `/api/health` | GET | Returns `{ status: "ok" }` | 27-29 |
| `/api/webhook/whatsapp` | POST | Parse WhatsApp → create order → audit → invoice | 32-83 |
| `/api/orders/:id` | PATCH | HITL correction → update order → conditional invoice | 86-118 |
| `/api/simulate` | POST | Generate mock simulation results → store → return | 121-149 |
| `/api/flows` | GET | List workflow definitions | 152-161 |
| `/api/flows` | POST | Create workflow definition | 163-174 |

## Test File Organization

**No test files detected.** There are no `*.test.*` or `*.spec.*` files anywhere in the repository. No testing configuration (`jest.config.*`, `vitest.config.*`) exists. The `package.json` has no test script.

If adding tests, the convention should follow:
- Co-located: `src/components/OrdersView.test.tsx` next to `src/components/OrdersView.tsx`
- Test runner: Recommend Vitest (already has Vite; minimal config overhead)
- Test library: Recommend React Testing Library

## Configuration File Purposes

### `package.json` Scripts
| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `tsx server.ts` | Start dev server with Vite HMR |
| `build` | `vite build && esbuild server.ts ...` | Build frontend + bundle server for production |
| `start` | `node dist/server.cjs` | Run production server |
| `clean` | `rm -rf dist` | Remove build artifacts |
| `lint` | `tsc --noEmit` | Type-check all TypeScript files |

### `vite.config.ts` Key Settings
- **Plugins:** `@vitejs/plugin-react`, `@tailwindcss/vite`
- **Path alias:** `@/` → project root
- **HMR/watching:** Controlled by `DISABLE_HMR` env var (for AI Studio compatibility)

### `tsconfig.json` Key Settings
- **Target:** ES2022
- **Module:** ESNext with bundler resolution
- **JSX:** `react-jsx`
- **Decorators:** `experimentalDecorators: true` with `useDefineForClassFields: false`
- **Path alias:** `@/*` → `./*`
- **Allow:** `allowJs: true`, `allowImportingTsExtensions: true`

## Where to Add New Code

**New View/Screen:**
- Create component in: `src/components/{Name}View.tsx`
- Add menu item entry in `MENU_ITEMS` array in `src/App.tsx`
- Add tab rendering in `src/App.tsx` switch statement (~line 260)

**New API Route:**
- Add handler in `server.ts` before the Vite/static middleware
- Follow existing pattern: `app.get|post|patch("/api/...", async (req, res) => { ... })`

**New Firestore Collection:**
- Add entity definition in `firebase-blueprint.json` (documentation)
- Add TypeScript interface in `src/types.ts`
- Add initial data in `seed.ts` if needed
- No migration needed (Firestore is schemaless)

**New TypeScript Type:**
- Add to `src/types.ts` — all shared types in one file

**New Utility Function:**
- Add to `src/utils.ts` if general-purpose, or create a new file in `src/lib/`

**New External Service Integration:**
- Create client module in `src/lib/{service-name}.ts`
- For server-only integrations: add import to `server.ts`

## Special Directories

| Directory | Purpose | Generated | Committed |
|-----------|---------|-----------|-----------|
| `dist/` | Build output (frontend + bundled server) | Yes | No (in `.gitignore`) |
| `node_modules/` | NPM dependencies | Yes | No (in `.gitignore`) |
| `.planning/` | GSD planning documents | Yes | Yes |
| `assets/` | AI Studio assets (`.aistudio/` subdir) | No | Yes |

---

*Structure analysis: 2026-06-21*
