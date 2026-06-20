# Codebase Concerns

**Analysis Date:** Sun Jun 21 2026

## 🔴 HIGH: Firestore Security Rules Wide Open

**Issue:** Both Firestore database instances use completely permissive rules allowing any read/write access.

**Files:**
- `firestore.rules` (lines 3-6, 8-11)

```text
match /databases/ai-studio-0c226e45-1671-429f-a15d-f7b5db246e6b/documents {
  match /{document=**} {
    allow read, write: if true;
  }
}
match /databases/(default)/documents {
  match /{document=**} {
    allow read, write: if true;
  }
}
```

**Impact:** Any client that knows the Firebase config (which is checked into the repo in `firebase-applet-config.json`) can read, write, or delete ALL data, including orders, invoices, parser audits, simulations, flows, and tenants. There is zero access control.

**Fix approach:**
1. Restrict rules to authenticated users at minimum: `allow read, write: if request.auth != null;`
2. Implement role-based access (owner, admin, operator).
3. Scope reads/writes to tenant-specific subcollections.
4. Add validation rules for field types and required fields.

---

## 🔴 HIGH: Firebase API Key and Config Committed to Repository

**Issue:** `firebase-applet-config.json` contains the live Firebase project configuration, including `apiKey`, `projectId`, `appId`, `authDomain`, and `firestoreDatabaseId`, committed in plaintext.

**Files:**
- `firebase-applet-config.json` (entire file)

```json
{
  "projectId": "gen-lang-client-0971155437",
  "appId": "1:498153626537:web:61bfaa06079d37e6b482b8",
  "apiKey": "AIzaSyDAvYDmoGgR31ZCeQu0lA0IL6YB53IVtTM",
  "authDomain": "gen-lang-client-0971155437.firebaseapp.com",
  ...
}
```

**Impact:** While Firebase API keys are somewhat restricted by Firebase project settings, exposing the project configuration makes it trivial for attackers to enumerate the project and attack the Firestore database via the open security rules. Combined with the open rules above, this is a critical vulnerability chain.

**Fix approach:**
1. Move all Firebase configuration to environment variables read at startup.
2. Add `firebase-applet-config.json` to `.gitignore` and use a template file instead.
3. Rotate the exposed API key in the Firebase Console.

---

## 🔴 HIGH: No Authentication on API Endpoints

**Issue:** The Express server (`server.ts`) has zero authentication or authorization middleware. All API routes are publicly accessible.

**Files:**
- `server.ts` (lines 27-148)

**Routes with no auth:**
- `GET /api/health` — Trivial, but serves as an attack surface
- `POST /api/webhook/whatsapp` — Accepts arbitrary order data from anyone
- `PATCH /api/orders/:id` — Anyone can modify any order
- `POST /api/simulate` — Anyone can trigger simulations
- `GET /api/flows` — Anyone can read flow definitions
- `POST /api/flows` — Anyone can create/modify flows

**Impact:** An unauthenticated attacker can create fake orders, modify existing orders, inject malicious flow definitions, or trigger unbounded simulations. Combined with the open Firestore rules, there is zero security boundary.

**Fix approach:**
1. Add API key or HMAC signature authentication middleware to all routes.
2. Validate webhook signatures according to WhatsApp Business API specifications.
3. Implement session-based or token-based auth for the UI-backed endpoints.
4. Add a global auth middleware with route whitelisting for public endpoints.

---

## 🔴 HIGH: GEMINI_API_KEY No Validation or Graceful Degradation

**Issue:** `src/lib/gemini.ts` reads `process.env.GEMINI_API_KEY` at module load time with zero validation. If the environment variable is missing, the `GoogleGenAI` client will fail at first use with an inscrutable error.

**Files:**
- `src/lib/gemini.ts` (line 8)

```typescript
const client = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
```

**Impact:** The server starts successfully even without the Gemini API key. The first webhook call will throw, returning a generic 500 error to the caller and silently consuming the Gemini parse failure. The error response returns a zero-confidence default object with no indication of the root cause.

**Fix approach:**
1. Validate `GEMINI_API_KEY` at server startup — crash early if missing.
2. Add a health check that verifies the Gemini API is reachable.
3. Implement a startup check script.

---

## 🔴 HIGH: Client-Side Firebase SDK Used Server-Side

**Issue:** `server.ts` imports the client-side `firebase` SDK (`firebase/app`, `firebase/firestore`) instead of `firebase-admin` for server-side Firestore access. The frontend `firebase-client.ts` also uses the client SDK with `experimentalForceLongPolling: true`.

**Files:**
- `server.ts` (lines 9-10, 17-18)
- `src/lib/firebase-client.ts` (lines 11-14)

```typescript
// server.ts — client SDK on the server
import { initializeApp } from "firebase/app";
import { getFirestore, collection, addDoc, serverTimestamp, doc, getDoc, updateDoc } from "firebase/firestore";
```

**Impact:** The client SDK is not designed for server environments. It lacks:
- Service account authentication (using API key, not admin credentials)
- Proper connection pooling
- Request-scoped credential isolation
- Admin SDK features like bypassing security rules (which would actually be needed since rules are open anyway)

**Fix approach:**
1. Replace `firebase` client imports with `firebase-admin` on the server.
2. Use service account credentials (via environment variable) instead of the client API key.
3. Remove `experimentalForceLongPolling` flag — it's unnecessary server-side.

---

## 🔴 HIGH: No Input Validation on Any API Endpoint

**Issue:** Express handlers accept `req.body` without validating structure, types, or constraints. The PATCH endpoint (`/api/orders/:id`) spreads `req.body` directly into the Firestore document update, making it possible to overwrite any field.

**Files:**
- `server.ts` (lines 33-83, 86-118, 121-149, 152-161, 163-174)

```typescript
// server.ts line 88-96 — accepts arbitrary fields
app.patch("/api/orders/:id", async (req, res) => {
  const { id } = req.params;
  const updates = req.body;
  // ... spreads updates directly into updateDoc
  await updateDoc(orderRef, { ...updates, updated_at: serverTimestamp() });
```

**Impact:** Attackers can overwrite `created_at`, `confidence`, `payment_status`, or inject malicious field values. No schema validation means data integrity cannot be guaranteed.

**Fix approach:**
1. Use input validation schemas (Zod, Yup, or Joi) for all request bodies.
2. Whitelist allowed fields for updates instead of spreading `req.body`.
3. Validate field types, ranges, and required constraints.

---

## 🟡 MEDIUM: Mock Simulation Returns Random Data

**Issue:** The `/api/simulate` endpoint uses `Math.random()` for every metric, generating entirely fictitious results.

**Files:**
- `server.ts` (lines 121-149)

```typescript
const results = {
  orders_processed: Math.floor(Math.random() * 500) + 100,
  parse_accuracy: 0.82 + Math.random() * 0.12,
  confidence_distribution: [...],
  avg_acknowledgement_time: (Math.random() * 8 + 2).toFixed(1),
  payment_conversion: (0.7 + Math.random() * 0.25).toFixed(2),
  // ...
};
```

**Impact:** Users and stakeholders see non-deterministic, unrealistic simulation results that cannot be reproduced or validated. Decisions based on these numbers have no basis in reality.

**Fix approach:**
1. Implement a proper discrete-event simulation engine.
2. At minimum, use seeded random values for reproducibility.
3. Add a disclaimer on the UI that results are stochastically generated.
4. Derive results from actual historical data or realistic queuing models.

---

## 🟡 MEDIUM: Hardcoded Pricing and Payment Links

**Issue:** Mock pricing and payment link generation URLs are hardcoded in two places.

**Files:**
- `server.ts` (lines 66, 71, 102, 107)

```typescript
const amount = (parsedData.items || []).length * 15; // Mock pricing RM15/item
payment_link: `https://duitnow.my/pay?to=ccam_mesh&amt=${amount}&ref=${orderRef.id}`,
```

**Impact:** All items are priced at RM15 regardless of actual menu pricing. Payment links point to a hardcoded URL with no TLS verification. This is mock data that could confuse users and is not suitable for any production use.

**Fix approach:**
1. Externalize item pricing to a configurable data source (Firestore prices collection or config).
2. Make payment link URL configurable via environment variable.
3. Implement actual pricing lookup from menu/inventory data.

---

## 🟡 MEDIUM: Overuse of `any` Types

**Issue:** The codebase uses `any` extensively, defeating TypeScript's type safety. 19+ instances in `src/`.

**Files:**
- `src/types.ts` (lines 24, 25, 26, 37, 38, 45, 48, 49, 77, 94, 103, 104) — 12 `any` type usages
- `src/components/SimulatorView.tsx` (line 19, 143)
- `src/components/HitlModal.tsx` (line 9)
- `src/components/CommandPalette.tsx` (line 28)
- `src/components/OrdersView.tsx` (line 109) — `as any` cast
- `src/App.tsx` (line 135)
- `src/utils.ts` (line 29)

**Impact:** Loss of compile-time type checking, potential runtime errors, poor developer experience with no autocompletion for typed fields, and masking of real bugs.

**Fix approach:**
1. Replace `any` with proper types in `src/types.ts` (use `Timestamp` for Firestore timestamps, proper chart data types, etc.).
2. Enable `noImplicitAny` in `tsconfig.json`.
3. Replace `as any` casts with proper type assertions.

---

## 🟡 MEDIUM: No TypeScript Strict Mode

**Issue:** `tsconfig.json` does not enable `strict: true`, `strictNullChecks`, `noImplicitAny`, `noUnusedLocals`, or `noUnusedParameters`.

**Files:**
- `tsconfig.json` (entire file)

**Impact:** The full suite of TypeScript safety features is disabled. Null-checks are not enforced, unused variables compile silently, and implicit `any` types are permitted. This leads to preventable runtime errors.

**Fix approach:**
1. Enable `"strict": true` in `tsconfig.json`.
2. Fix all resulting compilation errors.
3. Add lint script (`tsc --noEmit`) to CI pipeline.

---

## 🟡 MEDIUM: Non-Null Assertions `!` Used Unsafely

**Issue:** Two instances of the `!` non-null assertion operator without guaranteed element existence.

**Files:**
- `src/main.tsx` (line 6)

```typescript
createRoot(document.getElementById('root')!).render(
```

- `src/components/HitlModal.tsx` (line 115)

```typescript
onClick={() => onSave(order.id!, editedOrder)}
```

**Impact:** If the `#root` element doesn't exist, the crash is immediate and unrecoverable. If `order.id` is undefined (Firestore document ID missing), the PATCH request will fail with an error.

**Fix approach:**
1. Add null-check guards.
2. Provide fallback/error boundaries.
3. Use optional chaining with fallback for `order.id`.

---

## 🟡 MEDIUM: Empty Catch Blocks and Silent Error Handling

**Issue:** Several catch blocks either do nothing meaningful, only set loading state, or swallow errors without logging.

**Files:**
- `src/components/SimulatorView.tsx` (lines 35-37)
- `src/components/FlowsView.tsx` (lines 36-38)
- `src/components/FlowsView.tsx` (lines 68-69)
- `src/App.tsx` (lines 143-145)
- `src/App.tsx` (lines 114-118)
- `src/components/FinancialsView.tsx` (lines 26-27)

```typescript
// SimulatorView.tsx lines 35-37
} catch (e) {
  setRunning(false);
}

// FinancialsView.tsx lines 26-27
}, (error) => {
  console.error(error);
  setLoading(false);
});
```

**Impact:** Network failures, permission errors, and unexpected exceptions are silently suppressed. Users see no error feedback, and operations silently appear to succeed while failing.

**Fix approach:**
1. Surface user-friendly error messages for all catch blocks.
2. Log structured error info with context.
3. Implement a global error boundary for the React frontend.

---

## 🟡 MEDIUM: Zero Test Coverage

**Issue:** No test files, test framework configuration, or test-related dependencies exist.

**Files:**
- `package.json` (scripts section — only `tsc --noEmit` for lint)

**Search results:**
- No `*.test.*`, `*.spec.*`, `__tests__/` directories
- No `jest`, `vitest`, `mocha`, or `playwright` in dependencies
- No test command in `package.json`

**Impact:** No regression safety net. With 11 completed phases and no tests, any change risks breaking existing functionality. Refactoring or adding features is high-risk.

**Fix approach:**
1. Add a test framework (Vitest recommended for Vite projects).
2. Start with integration tests for API endpoints.
3. Add unit tests for utility functions and the Gemini parser.
4. Add component tests for critical views (OrdersView, HITL modal).

---

## 🟡 MEDIUM: No Structured Logging or Monitoring

**Issue:** All logging is via `console.log`/`console.error` with no structured format, log levels, or external monitoring integration.

**Files:**
- `server.ts` (lines 80, 192)
- `src/lib/gemini.ts` (line 45)
- `src/utils.ts` (line 41)
- `src/components/OrdersView.tsx` (line 55)
- `src/components/FinancialsView.tsx` (line 26)
- `src/components/FlowsView.tsx` (line 69)

**Impact:** Production debugging is impossible without log aggregation. No error tracking means the team doesn't know when things break. No metrics means performance regression goes undetected.

**Fix approach:**
1. Replace `console.log`/`console.error` with a structured logging library (e.g., `pino`, `winston`).
2. Integrate error tracking (Sentry).
3. Expose Prometheus metrics for API latency, error rates, queue depth.

---

## 🟡 MEDIUM: Hardcoded URLs in UI Components

**Issue:** Mock webhook URLs and node labels are hardcoded in the UI components.

**Files:**
- `src/components/FlowsView.tsx` (line 143)

```typescript
value="https://ccam-mesh.malaysia.ais/edge/v1/trigger"
```

- `src/components/SettingsView.tsx` (line 154)

```typescript
value="https://ccam-mesh.malaysia.ais/v1/webhook"
```

- `src/App.tsx` (line 238)

```typescript
NODE: KUALA_LUMPUR_01
```

**Impact:** These URLs don't resolve to actual services. If these become real endpoints, they'd need to be configurable per deployment environment. Hardcoded node labels misrepresent the infrastructure.

**Fix approach:**
1. Externalize all URLs to environment variables or configuration.
2. Remove or derive node labels from actual deployment metadata.

---

## 🟡 MEDIUM: Duplicated Code

**Issue:** `handleFirestoreError`, `OperationType`, and `FirestoreErrorInfo` are defined in both `src/utils.ts` and `src/components/OrdersView.tsx`, with slightly different implementations.

**Files:**
- `src/utils.ts` (lines 8-43)
- `src/components/OrdersView.tsx` (lines 12-57)

**Impact:** Code duplication leads to maintenance drift, inconsistency, and wasted bytes. The duplicate in `OrdersView.tsx` adds `tenantId` and `providerInfo` fields not present in the `utils.ts` version.

**Fix approach:**
1. Consolidate into a single shared utility module.
2. Import the shared version in `OrdersView.tsx`.
3. Add the extra fields (tenantId, providerInfo) to the shared version.

---

## 🟡 MEDIUM: No Docker / Docker Compose Configuration

**Issue:** Despite the UI documentation in `GovernanceView.tsx` describing Docker Compose setup, no `Dockerfile`, `docker-compose.yml`, or `.dockerignore` files exist in the repository.

**Files cited in UI:**
- `src/components/GovernanceView.tsx` (line 8-9)

```typescript
{ step: 'Prerequisites', items: ['Docker + Docker Compose', 'Python 3.11', ...] },
{ step: 'Setup Steps', items: ['Clone repo', 'Copy .env.example → .env', 'Run docker-compose up', ...] },
```

**Impact:** The documented deployment workflow doesn't work. New developers following the onboarding instructions will fail at the Docker step. There's no containerized deployment path.

**Fix approach:**
1. Create a `Dockerfile` for the Express/Next.js application.
2. Create a `docker-compose.yml` with API, frontend, and service dependencies.
3. Update `.dockerignore` for efficient builds.

---

## 🟡 MEDIUM: No CORS, Helmet, Rate Limiting, or Security Middleware

**Issue:** The Express server only uses `express.json()` as middleware. No security headers, CORS configuration, or rate limiting is implemented.

**Files:**
- `server.ts` (line 24)

```typescript
app.use(express.json());
// No: helmet(), cors(), rateLimit(), etc.
```

**Impact:** Vulnerable to common web attacks: CSRF, clickjacking, brute-force, and cross-origin data theft. No request throttling means the simulator endpoint can be hammered to exhaust Firestore write quotas.

**Fix approach:**
1. Add `helmet` for security headers.
2. Add `cors` with origin whitelist.
3. Add `express-rate-limit` for all routes, especially `/api/simulate` and `/api/webhook/whatsapp`.
4. Add request body size limits.

---

## 🟡 MEDIUM: Geminin 1.5 Flash Model Hardcoded

**Issue:** The Gemini model name is hardcoded to `"gemini-1.5-flash"` in the parser.

**Files:**
- `src/lib/gemini.ts` (line 33)

```typescript
model: "gemini-1.5-flash",
```

**Impact:** When Google deprecates or updates this model, the app will break. No ability to switch models without a code change. Cannot use newer/lower-cost models as they become available.

**Fix approach:**
1. Make model name configurable via environment variable.
2. Add model version negotiation with fallback.
3. Implement model selection logic based on message complexity.

---

## 🟡 MEDIUM: No Data Validation or Sanitization

**Issue:** User-submitted data (orders, flows) is stored directly without validation. Flow definitions are YAML strings with no schema validation.

**Files:**
- `server.ts` (lines 163-174) — flow definitions accepted without validation
- `src/components/FlowsView.tsx` (line 108) — YAML textarea with no schema enforcement

**Impact:** Malformed flow definitions can break the workflow engine. SQL injection-like YAML injection could corrupt data.

**Fix approach:**
1. Validate YAML schema before storing flows.
2. Validate order field types and constraints on the server.
3. Add client-side validation for required fields before submission.

---

## 🟡 MEDIUM: Redis and Persistence Claims Not Backed by Implementation

**Issue:** The UI claims "All orders backed by Redis persistence" (`OrdersView.tsx` line 260) and references Redis in `SystemsView.tsx` and `GovernanceView.tsx`, but no Redis connection or usage exists in the actual code.

**Files:**
- `src/components/OrdersView.tsx` (line 260)

```typescript
All orders backed by Redis persistence.
```

- `src/components/SystemsView.tsx` (lines 32, 372)

```typescript
{ component: 'Redis Sentinel', desc: 'Auto-promotion of replicas during partition.' }
```

**Impact:** Misleading documentation creates a false sense of reliability. The system has no caching layer, no queue, and no failover mechanism — all of which the documentation claims exist.

**Fix approach:**
1. Either implement Redis integration or remove claims from the UI.
2. If implementing, use Redis for: webhook deduplication, request caching, queue management, and session storage.

---

## 🟡 MEDIUM: Package.json Has Wrong Project Name

**Issue:** The package.json name is `"react-example"` suggesting this was scaffolded from a template and never updated.

**Files:**
- `package.json` (line 2)

```json
"name": "react-example",
```

**Impact:** Minor, but indicates the project may have other template defaults that weren't customized. Confusing for CI/CD and publishing pipelines.

**Fix approach:**
1. Update `package.json` `name` to `"ccam"` or similar.

---

## 🟢 LOW: No Error Boundary in React App

**Issue:** The React app (`App.tsx`, `main.tsx`) has no error boundary. Any runtime error in a component will crash the entire UI.

**Files:**
- `src/main.tsx` (all)
- `src/App.tsx` (all)

**Impact:** Users see a white screen on any unhandled error. No recovery mechanism.

**Fix approach:**
1. Implement a React Error Boundary component wrapping `<App />`.
2. Add a fallback UI with retry capability.

---

## 🟢 LOW: Health Check Is a No-Op

**Issue:** `GET /api/health` returns `{ status: "ok" }` without verifying any actual service dependencies.

**Files:**
- `server.ts` (lines 27-29)

```typescript
app.get("/api/health", (req, res) => {
  res.json({ status: "ok" });
});
```

**Impact:** Load balancers and orchestrators would route traffic to a server whose dependencies (Firestore, Gemini API) are down.

**Fix approach:**
1. Add dependency checks: Firestore connectivity, Gemini API reachability.
2. Return 503 status if dependencies are unavailable.

---

## 🟢 LOW: No Graceful Shutdown

**Issue:** The Express server has no `SIGTERM`/`SIGINT` handler for graceful shutdown.

**Files:**
- `server.ts` (line 191)

```typescript
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
// No process.on('SIGTERM', ...)
```

**Impact:** In containerized environments (Kubernetes/Docker), the server will drop in-flight requests when terminating.

**Fix approach:**
1. Add `process.on('SIGTERM')` and `process.on('SIGINT')` handlers.
2. Call `server.close()` and drain pending connections.

---

## 🟢 LOW: `seed.ts` Configured with Client SDK (Same Pattern as Server)

**Issue:** `seed.ts` uses the client Firebase SDK for a data-seeding script, without admin privileges.

**Files:**
- `seed.ts` (lines 1-8)

```typescript
import { initializeApp } from "firebase/app";
import { getFirestore, collection, addDoc, serverTimestamp } from "firebase/firestore";
```

**Impact:** The seed script will fail if Firestore rules are ever tightened (as they should be). The script relies on the currently-open rules.

**Fix approach:**
1. Convert `seed.ts` to use `firebase-admin` with a service account.
2. Make it a standalone script runnable in CI.

---

## 🟢 LOW: No CI/CD Pipeline Configuration

**Issue:** No GitHub Actions, workflow files, or CI configuration found in the repository.

**Impact:** No automated testing, linting, or deployment pipeline. Every deployment must be done manually.

**Fix approach:**
1. Add a `.github/workflows/` directory with CI/test/lint workflows.
2. Add build checks and automated deployment.

---

## 🟢 LOW: `.env.example` Contains Nonsensical Placeholders

**Issue:** The `.env.example` includes `MY_GEMINI_API_KEY` and `MY_APP_URL` as values, but it's unclear if these are actual expected values or placeholders.

**Files:**
- `.env.example` (lines 4, 9)

```
GEMINI_API_KEY="MY_GEMINI_API_KEY"
APP_URL="MY_APP_URL"
```

**Impact:** Developers might leave these placeholder values in their `.env` file, causing confusing failures.

**Fix approach:**
1. Use clear placeholder values: `GEMINI_API_KEY="<your-gemini-api-key>"`.
2. Add a startup validation that checks for placeholder strings.

---

## 🟢 LOW: No Data Retention / Cleanup Mechanism

**Issue:** Firestore collections (orders, audits, simulations, invoices, flows) accumulate data with no TTL, archival, or cleanup mechanism.

**Impact:** Firestore costs grow unboundedly. Query performance degrades over time. PDPA compliance requires data retention limits.

**Fix approach:**
1. Implement TTL-based data lifecycle management.
2. Add archival/cleanup jobs (Cloud Scheduler + Cloud Functions).
3. Add Firestore TTL policies.

---

## 🟢 LOW: Environment Variable Validation Gap

**Issue:** No validation of required environment variables at application startup.

**Files:**
- `server.ts` (all) — starts without checking required config
- `src/lib/gemini.ts` (line 8) — undeclared dependency on `GEMINI_API_KEY`

**Required env vars by code:**
- `GEMINI_API_KEY` — for Gemini AI API
- `NODE_ENV` — for production/dev mode switching (defaults to dev)

**Impact:** Application starts in a degraded state with missing configuration. Failures happen later at unpredictable points.

**Fix approach:**
1. Add a startup validation function that checks all required env vars.
2. Exit with a clear error message if any are missing.

---

*Concerns audit: Sun Jun 21 2026*
