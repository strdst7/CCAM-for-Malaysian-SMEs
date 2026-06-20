<!-- refreshed: 2026-06-21 -->
# Architecture

**Analysis Date:** 2026-06-21

## System Overview

```text
┌────────────────────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER (React SPA + Vite)                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │Dashboard │ │ Orders   │ │Simulator │ │Financials│ │  Flows   │ │ Settings │     │
│  │  View    │ │  View    │ │  View    │ │  View    │ │  View    │ │  View    │     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │
│       │            │            │            │            │            │           │
│  ┌────┴────────────┴────────────┴────────────┴────────────┴────────────┴────┐      │
│  │                      App Shell (App.tsx)                                  │      │
│  │  ┌───────────┐ ┌────────────────┐ ┌────────────────┐                     │      │
│  │  │  Sidebar  │ │  Command       │ │  HITL Modal    │                     │      │
│  │  │  Nav      │ │  Palette (⌘K)  │ │  (Correction)  │                     │      │
│  │  └───────────┘ └────────────────┘ └────────────────┘                     │      │
│  └──────────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────┬──────────────────────────────────────────────┘
                                       │
                              HTTP (fetch /api/*)
                                       │
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                       SERVER LAYER (Express + Vite SSR)                             │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐          │
│  │  server.ts  (Vite dev middleware / static prod serve)                │          │
│  │                                                                      │          │
│  │  GET  /api/health       → Health check                              │          │
│  │  POST /api/webhook/whatsapp → Parse WhatsApp → Create order          │          │
│  │  PATCH /api/orders/:id  → Human-in-the-Loop correction              │          │
│  │  POST /api/simulate     → Digital twin simulation                    │          │
│  │  GET  /api/flows        → List workflow DSL definitions              │          │
│  │  POST /api/flows        → Create workflow DSL definition             │          │
│  └──────────────────────────────────────────────────────────────────────┘          │
└──────────────────────────────────────┬──────────────────────────────────────────────┘
                                       │
                              Firebase Client SDK
                                       │
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                       DATA LAYER (Cloud Firestore)                                  │
│                                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │  orders  │ │ invoices │ │  flows   │ │simulations│ │parser_   │ │ tenants  │    │
│  │          │ │          │ │          │ │          │ │ audits   │ │          │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐                  │
│  │  Firestore Security Rules (permissive: read/write if true)   │                  │
│  └─────────────────────────────────────────────────────────────┘                  │
└────────────────────────────────────────────────────────────────────────────────────┘
                                       │
                              Gemini API (Cloud AI)
                                       │
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│                       AI LAYER (Gemini 1.5 Flash)                                   │
│                                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐                  │
│  │  parseWhatsAppMessage() → JSON-structured order extraction   │                  │
│  │  Model: gemini-1.5-flash                                     │                  │
│  │  SDK: @google/genai                                          │                  │
│  │  Confidence score: 0.0 - 1.0                                 │                  │
│  └──────────────────────────────────────────────────────────────┘                  │
└────────────────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| App Shell | Root layout, sidebar nav, tab routing, command palette, HITL modal, telemetry toast | `src/App.tsx` |
| DashboardView | KPI cards, parse volume chart, confidence heatmap, financial ROI, system efficiency | `src/components/DashboardView.tsx` |
| OrdersView | Live order buffer with Firestore `onSnapshot`, confidence bars, filter/search, correction trigger | `src/components/OrdersView.tsx` |
| SimulatorView | Digital twin config presets, `POST /api/simulate`, result visualization | `src/components/SimulatorView.tsx` |
| FinancialsView | Payment conversion funnel, invoice list from Firestore `onSnapshot` | `src/components/FinancialsView.tsx` |
| FlowsView | YAML workflow DSL editor, save/publish, active deployment registry | `src/components/FlowsView.tsx` |
| ComplianceView | Governance roadmap, PDPA compliance, encryption standards, risk register, audit trail | `src/components/ComplianceView.tsx` |
| GovernanceView | Tenant onboarding, HITL pipeline, SLO/SLA definitions, SRE playbooks, maintenance calendar | `src/components/GovernanceView.tsx` |
| SystemsView | Deployment topology, ERD, scaling benchmarks, CI/CD, API spec, STRIDE threat model | `src/components/SystemsView.tsx` |
| ReportsView | Pilot KPI tracking, weekly reports, baseline analysis comparison | `src/components/ReportsView.tsx` |
| SettingsView | Security matrix, data initialization, webhook config, onboarding wizard trigger | `src/components/SettingsView.tsx` |
| QAView | Sign-off matrix, test case registry, immutable audit trail viewer | `src/components/QAView.tsx` |
| OnboardingWizard | Multi-step tenant provisioning wizard (IDENTITY → SCHEMA → FLOW → COMPLETE) | `src/components/OnboardingWizard.tsx` |
| CommandPalette | ⌘K command palette for tab navigation and system actions | `src/components/CommandPalette.tsx` |
| HitlModal | Human-in-the-Loop order correction modal | `src/components/HitlModal.tsx` |
| Gemini Client | WhatsApp message parsing via Gemini 1.5 Flash | `src/lib/gemini.ts` |
| Firebase Client | Firestore + Auth initialization | `src/lib/firebase-client.ts` |
| Utils | CSS class merging (`cn()`) and Firestore error handler | `src/utils.ts` |
| Types | Order, Invoice, ParserAudit, InventoryItem, SimulationConfig/Result, FlowDefinition, PilotMetrics, Report | `src/types.ts` |
| Server | Express API server (health, webhook, orders, simulate, flows) + Vite/static serving | `server.ts` |
| Seed | CLI script to populate initial demo data (orders + flows) | `seed.ts` |

## Pattern Overview

**Overall:** Monolithic SPA with colocated Express API backend. Single codebase, single `package.json`, single `tsconfig.json`. Both frontend and backend run from the same process in development.

**Key Characteristics:**
- **Server-side rendering via Vite middleware** — Express serves the React SPA via Vite's middleware in development, or static files in production
- **Firebase Client SDK used server-side** — `server.ts` uses `firebase` (client SDK) to interact with Firestore from Node.js (not `firebase-admin`)
- **Gemini AI integration via `@google/genai` SDK** — used for structured data extraction from natural language WhatsApp messages
- **`onSnapshot` real-time listeners** — OrdersView and FinancialsView use Firestore `onSnapshot` for live updates
- **Dark cyberpunk UI theme** — `#050505` background, `#00FF9C` accent (green), `Inter`/`JetBrains Mono` fonts, Tailwind v4
- **No state management library** — local `useState`/`useEffect` only, no Redux or Zustand
- **No testing framework detected** — no test files, no jest/vitest config

## Layers

### Client Layer (React SPA)
- **Purpose:** Renders the operations dashboard for Malaysian F&B order management
- **Location:** `src/`
- **Contains:** 11 view components, 3 shared components (CommandPalette, HitlModal, OnboardingWizard), 2 lib modules, types, utils, styles
- **Depends on:** Firebase Client SDK (Firestore `onSnapshot` real-time listeners), Gemini Client SDK (indirectly via server API)
- **Used by:** End users (SME operators, managers)

### Server Layer (Express + Vite)
- **Purpose:** REST API for webhook ingestion, order correction, simulation, and flow management. Serves the SPA.
- **Location:** `server.ts`
- **Contains:** 6 REST endpoints, Vite dev middleware, production static file serving
- **Depends on:** Firebase Client SDK (`firebase/app`, `firebase/firestore`), `@google/genai` (via `src/lib/gemini.ts`), `express`, `vite`
- **Used by:** Frontend SPA (via `fetch`), external webhook callers

### Data Layer (Cloud Firestore)
- **Purpose:** Persistent storage for orders, invoices, flows, simulations, parser audits, tenants
- **Location:** Firebase project `gen-lang-client-0971155437`, database `ai-studio-0c226e45-1671-429f-a15d-f7b5db246e6b`
- **Contains:** 6 collections
- **Depends on:** Firebase Client SDK initialized in both `server.ts` and `src/lib/firebase-client.ts`
- **Data model defined in:** `firebase-blueprint.json`

### AI Layer (Gemini 1.5 Flash)
- **Purpose:** Natural language understanding for WhatsApp message parsing
- **Location:** `src/lib/gemini.ts`
- **Contains:** Single function `parseWhatsAppMessage()` that calls Gemini with structured JSON extraction prompt
- **Depends on:** `@google/genai` SDK, `GEMINI_API_KEY` environment variable
- **Used by:** Server webhook handler (`server.ts:32`)

## Data Flow

### Primary Request Path: WhatsApp → Order → Invoice

1. **WhatsApp message received** at `POST /api/webhook/whatsapp` (`server.ts:32`)
2. **Gemini parsing** via `parseWhatsAppMessage()` (`src/lib/gemini.ts:10`) — extracts customer_name, items, delivery_address, pickup_time, payment_method, confidence
3. **Confidence check** (`server.ts:41`): if `confidence >= 0.85`, auto-confirm; otherwise mark as 'new'
4. **Order creation** in Firestore `orders` collection (`server.ts:53`)
5. **Parser audit record** in `parser_audits` collection (`server.ts:56`)
6. **Invoice generation** if auto-confirmed (`server.ts:65`) — creates invoice with DuitNow payment link in `invoices` collection
7. **Response** returns order ID and parsed data to caller

### Correction Path (Human-in-the-Loop)

1. **Frontend triggers** HITL modal via `onCorrect` callback in OrdersView (`src/components/OrdersView.tsx:190`)
2. **Operator edits** order fields in HitlModal (`src/components/HitlModal.tsx`)
3. **Save sends** `PATCH /api/orders/:id` with corrected fields (`server.ts:86`)
4. **Server updates** order in Firestore and generates invoice if newly confirmed
5. **Response** returns success

### Simulation Path

1. **User configures** scenario in SimulatorView (`src/components/SimulatorView.tsx`)
2. **POST /api/simulate** with config (`server.ts:121`)
3. **Server generates** mock simulation results (orders_processed, parse_accuracy, confidence_distribution, etc.)
4. **Result stored** in `simulations` collection
5. **Response** returns results to frontend for chart rendering

### State Management
- **Firestore real-time sync:** Orders (`orders`) and invoices use `onSnapshot` for live updates without polling
- **Local component state:** All UI state (active tab, filters, search, sidebar) managed via `useState` in `App.tsx`
- **No global state store:** No React Context, Redux, or Zustand. Props passed down from App.tsx to children.
- **Health polling:** `App.tsx` polls `GET /api/health` every 15 seconds to display sync status

## Key Abstractions

### App Shell (`src/App.tsx`)
- **Purpose:** Root orchestrator component managing navigation, global overlays, and telemetry
- **Pattern:** React functional component with `useState` for activeTab, sidebar state, notification, correction order
- **Sidebar:** 10 menu items across 4 categories (Insights, Governance, Operations, Automation)
- **Global overlays:** HITL modal, Command Palette (⌘K), telemetry notification toast

### Gemini Parser (`src/lib/gemini.ts`)
- **Purpose:** Structured data extraction from WhatsApp natural language
- **Pattern:** Zero-shot JSON extraction via Gemini 1.5 Flash
- **Prompt:** Instructs model to extract Malaysian F&B order details with JSON schema
- **Fallback:** Returns null/default values on error
- **Extraction:** Uses regex `/\{[\s\S]*\}/` to extract JSON from markdown-wrapped responses

### View Components (`src/components/*View.tsx`)
- **Pattern:** Each view is a named export default function, receives optional props (`triggerRun`, `triggerCreate`, `onCorrect`)
- **Data access:** Components either use Firestore `onSnapshot` directly or call server APIs via `fetch`
- **Styling:** Tailwind CSS with `cn()` helper from `src/utils.ts`

### Firebase Client (`src/lib/firebase-client.ts`)
- **Purpose:** Singleton Firebase app initialization
- **Pattern:** Module-level singleton — `initializeApp()` called once at import time
- **Exports:** `db` (Firestore instance with long polling), `auth` (Auth instance)
- **Config:** Loaded from `firebase-applet-config.json`

## Entry Points

| Entry Point | Location | Triggers | Responsibilities |
|-------------|----------|----------|------------------|
| Application start | `server.ts:196` | `tsx server.ts` / `npm run dev` | Initialize Express, Firebase, Vite middleware; listen on port 3000 |
| SPA mount | `src/main.tsx` | Browser loads `index.html` | Mount React app to `#root` |
| Webhook ingestion | `server.ts:32` | External HTTP POST | Parse WhatsApp message, create order + audit, generate invoice |
| Order correction | `server.ts:86` | Frontend PATCH request | Update order in Firestore, conditionally generate invoice |
| Simulation | `server.ts:121` | Frontend POST request | Generate mock simulation results, store in Firestore |
| Flows API | `server.ts:152-174` | Frontend GET/POST requests | List and create workflow DSL definitions |
| Seed data | `seed.ts:58` | `tsx seed.ts` | Populate initial demo orders and flows |

## Architectural Constraints

- **No separate backend directory:** API routes are colocated in `server.ts` at the root level alongside the frontend `src/` directory (no `api/` or `server/` folder)
- **Firebase Client SDK in Node.js:** Uses `firebase` (web client SDK) server-side instead of `firebase-admin`. This means the server initializes Firebase with the same config as the client, including the web API key
- **Permissive Firestore security:** `firestore.rules` allows `read, write: if true` on all documents — no auth checks
- **Single-threaded:** Express runs single-threaded; no worker threads for CPU-intensive work
- **No Redis/queue backend:** Despite mentions in the UI, there is no actual Redis or job queue. All processing is synchronous within the Express request
- **Mock simulation data:** The `/api/simulate` endpoint generates random data, not actual digital twin computations
- **No authentication:** No auth middleware on any API route; Firebase Auth is initialized but unused in the UI flow
- **No database migrations:** Schema defined only in `firebase-blueprint.json` (design document); Firestore is schemaless

## Anti-Patterns

### Firestore Client SDK in Node.js Backend
- **What happens:** `server.ts` uses `firebase` (web client SDK) imports like `initializeApp`, `getFirestore`, `addDoc`, `collection`, `doc`, `getDoc`, `updateDoc`
- **Why it's wrong:** The web client SDK is designed for browser environments and includes WebSocket-based real-time listeners. In Node.js, `firebase-admin` is the proper SDK with service account auth, better performance, and no unnecessary browser polyfills
- **Do this instead:** Use `firebase-admin` with a service account credential for server-side Firestore access (`src/lib/firebase-admin.ts`)

### Permissive Firestore Rules
- **What happens:** `allow read, write: if true` on all paths in `firestore.rules`
- **Why it's wrong:** Every client with the Firebase config can read/write all data. No tenant isolation, no auth checks, no data validation
- **Do this instead:** Implement proper security rules checking `request.auth` and tenant IDs

### Mock Simulation Returned as Real
- **What happens:** `POST /api/simulate` returns `Math.random()` generated results as if they were real simulation output
- **Why it's wrong:** This creates a false sense of analytical capability. The confidence distribution, accuracy, and revenue estimates are entirely fabricated
- **Do this instead:** Either build an actual simulation engine or clearly label results as "estimates" in the UI

### API Key in Client-Facing Config
- **What happens:** `firebase-applet-config.json` contains the Firebase `apiKey` and is served to the client
- **Why it's wrong:** While Firebase API keys are not secrets per se, having sensitive project config in a JSON file that's accessible via the client exposes the project ID and configuration
- **Do this instead:** This is acceptable for Firebase (API keys are meant to be client-side), but ensure App Check is configured to prevent abuse

## Error Handling

**Strategy:** Try/catch with generic 500 responses

**Patterns:**
- **Server errors:** Caught in try/catch blocks around each route handler (`server.ts:79`, `115`, `159`). Returns `{ error: "Internal Server Error" }` or `{ error: error.message }`
- **Gemini errors:** Caught in `parseWhatsAppMessage()` (`src/lib/gemini.ts:44`). Returns fallback empty parsed object with `confidence: 0`
- **Firestore errors:** Logged via `handleFirestoreError()` utility (`src/utils.ts:29`) which enriches error context with auth info and operation type
- **Frontend fetch errors:** Caught in individual components with `console.error` and state updates (e.g., `setRunning(false)` in SimulatorView)
- **Network health:** App.tsx polls `/api/health` every 15s and shows `SYNC_LIVE` / `CONNECTION_OFFLINE` badge

## Cross-Cutting Concerns

**Logging:** `console.error` and `console.log` throughout. No structured logging library.
**Validation:** No input validation beyond empty string check on webhook message (`server.ts:35`)
**Authentication:** None implemented on API or Firestore. Firebase Auth initialized in `firebase-client.ts` but not used for gating.
**Theming:** Tailwind CSS v4 with custom `@theme` block defining `--font-sans` (Inter) and `--font-mono` (JetBrains Mono). Dark color scheme with `#050505` background and `#00FF9C` accent.

---

*Architecture analysis: 2026-06-21*
