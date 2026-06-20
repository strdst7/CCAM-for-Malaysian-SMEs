# External Integrations

**Analysis Date:** 2026-06-21

## APIs & External Services

### Google Gemini AI API

| Property | Value |
|----------|-------|
| **SDK/Client** | `@google/genai` ^2.4.0 (`GoogleGenAI` class) |
| **Auth** | `GEMINI_API_KEY` environment variable |
| **Model** | `gemini-1.5-flash` (hardcoded in `src/lib/gemini.ts:33`) |
| **Usage** | WhatsApp message parsing for F&B order extraction |
| **Endpoint** | `client.models.generateContent()` |
| **File** | `src/lib/gemini.ts` |

**Integration Pattern:** Direct SDK client initialization in module scope:
```typescript
const client = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
```

The `parseWhatsAppMessage()` function sends a structured prompt with JSON schema instructions to Gemini, then parses the response text extracting JSON from markdown code block markers. On failure, returns a fallback null object.

**Prompt Structure:**
- System persona: "parsing engine for Malaysian F&B order automation system called CCAM"
- Extracts: customer_name, items (name + qty), delivery_address, pickup_time, payment_method, confidence
- Malaysian context: Nasi Lemak, Teh Tarik, RM, etc.

### Firebase Platform

| Property | Value |
|----------|-------|
| **SDK/Client** | `firebase` ^12.15.0 (Client SDK), `firebase-admin` ^14.0.0 (Admin SDK) |
| **Auth Config** | `firebase-applet-config.json` — static JSON config file |
| **Project ID** | `gen-lang-client-0971155437` |
| **App ID** | `1:498153626537:web:61bfaa06079d37e6b482b8` |
| **Firestore DB ID** | `ai-studio-0c226e45-1671-429f-a15d-f7b5db246e6b` |
| **Storage Bucket** | `gen-lang-client-0971155437.firebasestorage.app` |

**Initialization — Server-side (`server.ts`):**
```typescript
const firebaseConfig = JSON.parse(fs.readFileSync("./firebase-applet-config.json", "utf8"));
const app = initializeApp(firebaseConfig);
const db = getFirestore(app, firebaseConfig.firestoreDatabaseId);
```

**Initialization — Client-side (`src/lib/firebase-client.ts`):**
```typescript
import firebaseConfig from "../../firebase-applet-config.json";
const app = initializeApp(firebaseConfig);
export const db = initializeFirestore(app, { experimentalForceLongPolling: true }, firebaseConfig.firestoreDatabaseId);
export const auth = getAuth(app);
```

### Firestore Database

| Property | Value |
|----------|-------|
| **Type** | Cloud Firestore (native mode) |
| **Client** | Firebase Web Client SDK (both server and client) |
| **Collections** (from `firebase-blueprint.json` and code) | `orders`, `simulations`, `invoices`, `flows`, `parser_audits` |
| **Security Rules** | `firestore.rules` — currently wide open (`allow read, write: if true` for all documents) |

**Collection Schema Summary (from `firebase-blueprint.json`):**

| Collection | Entity | Key Fields |
|-----------|--------|------------|
| `orders` | Order | tenant_id, customer_name, customer_phone, items (array), items_json, total_estimate, delivery_address, pickup_time, payment_method, payment_status, status, confidence, raw_message, created_at, updated_at |
| `simulations` | Simulation | config (object), results (object), created_at |
| `invoices` | Invoice | order_id, customer_name, amount, payment_link, status, created_at, due_date |
| `flows` | Flow | name, definition (YAML string), created_at |
| `parser_audits` | ParserAudit | message_id, order_id, raw_text, parsed_json, confidence, corrected_by, correction_timestamp, created_at |

**Access Patterns:**

| Operation | Where | Pattern |
|-----------|-------|---------|
| Write order | `server.ts:53` | `addDoc(collection(db, "orders"), orderData)` |
| Write audit | `server.ts:56` | `addDoc(collection(db, "parser_audits"), ...)` |
| Write invoice | `server.ts:67` | `addDoc(collection(db, "invoices"), ...)` |
| Read/Update order | `server.ts:91-96` | `getDoc`, `updateDoc` |
| Read flows (GET) | `server.ts:154-155` | `getDocs(collection(db, "flows"))` |
| Write flows (POST) | `server.ts:166` | `addDoc(collection(db, "flows"), ...)` |
| Write simulation | `server.ts:142-146` | `addDoc(collection(db, "simulations"), ...)` |
| Listen orders (realtime) | `src/components/OrdersView.tsx:67-76` | `onSnapshot(query(collection(db, 'orders'), orderBy('created_at', 'desc'), limit(50)))` |
| Listen invoices (realtime) | `src/components/FinancialsView.tsx:21-29` | `onSnapshot(query(collection(db, 'invoices'), orderBy('created_at', 'desc'), limit(20)))` |
| Health check | `src/App.tsx:113` | `getDocFromServer(doc(db, 'system', 'health'))` |

### Firebase Authentication

| Property | Value |
|----------|-------|
| **SDK** | `firebase/auth` via Firebase Client SDK |
| **Integration** | `src/lib/firebase-client.ts` exports `auth = getAuth(app)` |
| **Usage** | `src/utils.ts` and `src/components/OrdersView.tsx` check `auth.currentUser?.uid`, `auth.currentUser?.email`, etc. for error reporting context |
| **Actual auth state** | Authentication is initialized but never explicitly required — Firestore rules are wide open, there is no login flow in the UI |

Auth is used only for diagnostic context in `handleFirestoreError` utilities. No sign-in/sign-up flow, no route guards, no auth-dependent rendering exist in the current codebase.

## REST API Endpoints (Express Server)

All endpoints are defined in `server.ts` and served on **port 3000**.

| Method | Path | Purpose | Request Body | Response |
|--------|------|---------|-------------|----------|
| `GET` | `/api/health` | Health check | — | `{ status: "ok" }` |
| `POST` | `/api/webhook/whatsapp` | Simulated WhatsApp webhook | `{ message: string, customer_phone?: string }` | `{ id: string, ...parsedData }` |
| `PATCH` | `/api/orders/:id` | Update order (HITL correction) | Partial Order fields + status | `{ success: true }` |
| `POST` | `/api/simulate` | Run digital twin simulation | `SimulationConfig` object | `{ id: string, results: {...} }` |
| `GET` | `/api/flows` | List all workflow definitions | — | `FlowDefinition[]` |
| `POST` | `/api/flows` | Create new workflow definition | `{ name, definition, is_active }` | `{ id: string }` |

**API Integration Pattern:**
- Server-side: direct Express handler functions using Firebase Client SDK
- Client-side (React components): `fetch('/api/...')` calls with JSON headers
- Example from `src/App.tsx:137`: `fetch(\`/api/orders/${id}\`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(...) })`
- Example from `src/components/SimulatorView.tsx:25`: `fetch('/api/simulate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(simConfig) })`

### Frontend ↔ Backend Integration

The Express server acts as both API server and static file server:

1. **Development mode** (`NODE_ENV !== "production"`):
   - Express creates a Vite dev server in middleware mode (`createViteServer({ server: { middlewareMode: true } })`)
   - Vite middleware serves the React SPA with HMR support
   - API routes are served on the same port alongside the SPA

2. **Production mode**:
   - Build outputs to `dist/` directory (via `vite build`)
   - Express serves `dist/` as static files (`express.static(distPath)`)
   - All unmatched routes return `dist/index.html` (SPA fallback)

## Caching

- **Redis:** Referenced in UI (`OrdersView.tsx:260` mentions "All orders backed by Redis persistence", `SystemsView.tsx` references Redis sharding/scaling). However, **no Redis client or connection exists in the actual codebase**. Redis integration is purely speculative UI mock content.
- **No caching layer** is currently implemented at the application level.

## Monitoring & Observability

**Error Tracking:**
- None. No Sentry, DataDog, or similar SDKs.
- Errors are logged via `console.error` only.

**Logs:**
- `console.log` and `console.error` throughout server and client code.
- Structured error info in `src/utils.ts:handleFirestoreError()` — logs `FirestoreErrorInfo` JSON objects with auth context.

**Health Monitoring:**
- Client-side health polling in `src/App.tsx:122-131`: polls `/api/health` every 15 seconds. Updates sync status indicator (`SYNC_LIVE` / `CONNECTION_OFFLINE`).

## CI/CD & Deployment

**Hosting:**
- **Google AI Studio App Hosting** — The app is deployed as an AI Studio applet. `APP_URL` is injected at runtime by the AI Studio platform as a Cloud Run service URL.

**CI Pipeline:**
- **Not detected** — No GitHub Actions, GitLab CI, or other CI configuration files found in the repository. The `SystemsView.tsx` component references CI/CD pipeline steps (CI_BUILD, UNIT_TEST, SEC_SCAN, K8S_DEPLOY) and GitHub Actions, but these are UI mock/design concepts only.

**Docker:**
- **Not detected** — No `Dockerfile`, `docker-compose.yml`, or `.dockerignore` found. The `GovernanceView.tsx` component references Docker + Docker Compose in dev setup instructions, but no actual configs exist.

## Webhooks & Callbacks

**Incoming:**
- `/api/webhook/whatsapp` — Simulated WhatsApp webhook endpoint (`server.ts:32`).
- Accepts `{ message, customer_phone }` JSON body.
- Returns parsed order data or error response.
- Currently a development mock — no actual WhatsApp Business API HMAC verification implemented (though referenced in UI as "HMAC signature" and "HMAC-256" validation).

**Outgoing:**
- **DuitNow payment links** — Generated dynamically in `server.ts:71`: `\`https://duitnow.my/pay?to=ccam_mesh&amt=${amount}&ref=${orderRef.id}\``
- These are mock payment URLs, not real DuitNow API integrations.

## Environment Configuration

**Required environment variables:**

| Variable | Source | Used In | Purpose |
|----------|--------|---------|---------|
| `GEMINI_API_KEY` | `.env` file / AI Studio secrets | `src/lib/gemini.ts:8` | Gemini API authentication |
| `APP_URL` | AI Studio runtime injection | — | Self-referencing URL (defined in `.env.example`, not used in current code) |
| `DISABLE_HMR` | Optional environment | `vite.config.ts:17-19` | Disables Vite HMR and file watching for AI Studio agent compatibility |
| `NODE_ENV` | Runtime environment | `server.ts:177` | Switches between dev (Vite middleware) and production (static files) modes |

**Secrets location:**
- Gemini API key: user-configured in AI Studio Secrets panel or local `.env` file.
- Firebase config: `firebase-applet-config.json` (committed to repo — contains API key, project ID).
- `.env*` files are gitignored (only `.env.example` is tracked).

**Security note:** The Firebase API key in `firebase-applet-config.json` is committed to the repository. This is a client-side API key (Firebase API keys are designed to be public, but should be restricted by Firebase Console settings and App Check enforcement).

## Integration Patterns (Summary)

| Pattern | Used For | Files |
|---------|----------|-------|
| SDK Client (Gemini) | LLM inference — order parsing | `src/lib/gemini.ts` |
| SDK Client (Firebase) | Firestore CRUD + Auth | `server.ts`, `src/lib/firebase-client.ts`, all view components |
| REST (fetch) | Client ↔ Express API | `src/App.tsx`, `SimulatorView.tsx`, `FlowsView.tsx` |
| Realtime listener (onSnapshot) | Live order/invoice updates | `OrdersView.tsx`, `FinancialsView.tsx` |
| Health polling (setInterval + fetch) | Connectivity monitoring | `src/App.tsx` |
| Static JSON config file | Firebase credentials | `firebase-applet-config.json` |
| Static JSON schema definition | Data model blueprint | `firebase-blueprint.json` |

## Test Infrastructure Integrations

**Not detected:**
- No test runner (Jest, Vitest, Mocha, etc.)
- No test files (`.test.ts`, `.spec.ts`)
- No test configuration files
- No E2E testing tools (Cypress, Playwright)
- No mocking frameworks

The `QAView.tsx` component displays a visual QA test case matrix (with hardcoded test results) but this is a UI mock/display component only — no actual test automation exists.

## Missing / Speculative Integrations (UI-only Mocks)

The following integrations are referenced in UI components or design documents but are **not implemented** in the codebase:

| Integration | Referenced In | Actual Status |
|-------------|---------------|---------------|
| Redis caching | `OrdersView.tsx`, `SystemsView.tsx` | Not implemented — no Redis client |
| Docker / Docker Compose | `GovernanceView.tsx` | Not present — no Dockerfile |
| Kubernetes (K8s) | `SystemsView.tsx` | Not present — no K8s manifests |
| GitHub Actions CI | `SystemsView.tsx` | Not present — no CI configs |
| GitHub Actions CI | `SystemsView.tsx` | Not present — no CI configs |
| WhatsApp Business API | `server.ts` webhook endpoint | Mock only — no real WhatsApp API integration |
| DuitNow payment API | `server.ts` invoice generation | Mock payment links only |
| POS Connector (StoreHub, Slurp, Qashier) | `SystemsView.tsx` | Design concept only |
| Prometheus monitoring | `SystemsView.tsx` | Not implemented |
| Alembic DB migrations (Python) | `GovernanceView.tsx` | Not present — project is TypeScript/Node.js |
| Mobile offline sync (SQLite) | `SystemsView.tsx` | Design concept only |

---

*Integration audit: 2026-06-21*
