# Coding Conventions

**Analysis Date:** 2026-06-21

**Project:** CCAM (Contextual Conversational Automation Mesh) — Firebase AI Studio applet for Malaysian F&B WhatsApp order automation with Gemini AI parsing.

---

## Naming Patterns

**Files:**
- **Components:** PascalCase — `DashboardView.tsx`, `HitlModal.tsx`, `CommandPalette.tsx`
- **Utilities/helpers:** camelCase — `utils.ts`, `firebase-client.ts`, `gemini.ts`
- **Types:** camelCase — `types.ts`
- **Entry points:** lowercase — `server.ts`, `seed.ts`, `index.html`
- **Config:** kebab-case — `vite.config.ts`, `firebase-applet-config.json`, `firebase-blueprint.json`

**Functions:**
- **React components:** PascalCase default exports — `export default function DashboardView()`
- **Utility functions:** camelCase — `cn()`, `handleFirestoreError()`, `parseWhatsAppMessage()`
- **Event handlers:** camelCase prefixed with `handle` — `handleCorrect()`, `handleKeyDown`, `handleTriggerAction()`, `handleListKeyDown()`, `handleIdentitySubmit()`
- **Data fetching:** camelCase prefixed with `fetch` — `fetchFlows()`, or `runSimulation()`
- **State initializers:** camelCase — `initializeSampleData()`

**Variables:**
- **All variables:** camelCase — `activeTab`, `sidebarOpen`, `searchQuery`, `editedOrder`, `simConfig`
- **Constants (module-level arrays):** UPPER_SNAKE_CASE — `MENU_ITEMS`, `systemActions`, `tabCommands`
- **Boolean state:** `loading`, `running`, `seeding`, `isOpen`, `sidebarOpen`
- **Refs:** camelCase suffixed with `Ref` — `inputRef`, `containerRef`, `nameInputRef`

**Types/Interfaces:**
- **Interfaces:** PascalCase — `Order`, `Invoice`, `OrderItem`, `FlowDefinition`, `SimulationConfig`, `PilotMetrics`
- **Enums:** PascalCase — `OperationType` (member keys in UPPER_SNAKE_CASE)
- **Type aliases (union):** camelCase strings — `'live' | 'offline'`, `'all' | 'correction'`, `'success' | 'info' | 'error'`
- **Props interfaces:** PascalCase suffixed with `Props` — `HitlModalProps`, `CommandPaletteProps`, `FlowsViewProps`, `SimulatorViewProps`

---

## Code Style

**TypeScript Configuration (`tsconfig.json`):**
- Target: `ES2022`
- Module: `ESNext` with bundler module resolution
- JSX: `react-jsx`
- Strict mode: **NOT enabled** (no `strict: true`)
- `skipLibCheck: true`
- `isolatedModules: true`
- `useDefineForClassFields: false`
- `experimentalDecorators: true`
- Allow JS: `true`
- Path alias: `@/*` maps to `./*`
- Allow importing TS extensions: `true`
- No emit (`noEmit: true`)

**Formatting:**
- No Prettier configuration detected — project uses default editor formatting
- 2-space indentation observed throughout all files
- Semicolons: consistently used (end every statement with `;`)
- Single quotes: consistently used in import/export statements
- Trailing commas: consistently used in multi-line object/array literals
- Line breaks: components use generous whitespace (2-3 blank lines between logical sections)

**Linting:**
- No ESLint configuration detected
- The only lint check is `"lint": "tsc --noEmit"` in `package.json` — TypeScript compiler type-checking only

**Key style patterns observed:**
```typescript
// Import pattern — grouped by source
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../utils';

// Props destructuring inline
export default function OrdersView({ onCorrect }: { onCorrect: (o: Order) => void }) {
```

---

## Import Organization

**Order pattern observed across all files:**
1. **React/Framework imports** — `react`, `motion/react`, `lucide-react`
2. **Project utilities** — `../utils`, `../types`
3. **Firebase SDK** — `firebase/firestore`, `firebase/auth`
4. **Project libs** — `../lib/firebase-client`
5. **Sibling components** — `./DashboardView`, `./OrdersView`
6. **CSS** — `../index.css` (only in `main.tsx`)

**Path Aliases:**
- `@/*` maps to `./*` (configured in `tsconfig.json` and `vite.config.ts`) — **but not used in any source file.** All imports use relative paths (`../`, `./`).

**Import style:**
```typescript
// Named imports from third-party libs
import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../utils';

// Default imports for components
import DashboardView from './components/DashboardView';
import HitlModal from './components/HitlModal';
```

---

## React Component Patterns

**Component Structure:**
- All components are function components (no class components)
- Use default exports exclusively
- Props typed inline or via interface defined above component
- Consistent motion/animation wrapper using `motion.div` with `initial`/`animate`/`exit` props

**State Management:**
- Local state only via `useState` — no global state library
- No Redux, Zustand, or Context API used
- Sync status tracked with `syncStatus` state in `App.tsx`
- Notification toasts managed via local state
- Data fetched via `useEffect` with `onSnapshot` Firestore listeners or `fetch()` API calls

**Component Props Pattern:**
```typescript
// Interface approach (preferred for complex props)
interface HitlModalProps {
  order: Order;
  onClose: () => void;
  onSave: (id: string, updates: any) => void;
}
export default function HitlModal({ order, onClose, onSave }: HitlModalProps) { ... }

// Inline type approach (for simple props)
export default function OrdersView({ onCorrect }: { onCorrect: (o: Order) => void }) { ... }
```

**Animation convention:**
```typescript
// Every view uses this pattern:
<motion.div
  initial={{ opacity: 0, y: 10 }}
  animate={{ opacity: 1, y: 0 }}
  className="space-y-8 pb-20"
>
```

---

## Error Handling Conventions

**Current error handling patterns observed:**

1. **try/catch with console.error:**
```typescript
try {
  // operation...
} catch (error) {
  console.error("Webhook Error:", error);
  res.status(500).json({ error: "Internal Server Error" });
}
```

2. **Firestore error wrapper (local pattern in `OrdersView.tsx` and `utils.ts`):**
```typescript
function handleFirestoreError(error: unknown, operationType: OperationType, path: string | null) {
  const errInfo: FirestoreErrorInfo = {
    error: error instanceof Error ? error.message : String(error),
    authInfo: {
      userId: auth.currentUser?.uid,
      email: auth.currentUser?.email,
      // ...
    },
    operationType,
    path
  }
  console.error('Firestore Error: ', JSON.stringify(errInfo));
  throw new Error(JSON.stringify(errInfo));
}
```

3. **Express error responses:**
- 400 for bad requests: `res.status(400).json({ error: "Message is required" })`
- 500 for server errors: `res.status(500).json({ error: error.message })`

4. **Frontend fetch error handling:**
```typescript
try {
  const res = await fetch('/api/health');
  setSyncStatus(res.ok ? 'live' : 'offline');
} catch {
  setSyncStatus('offline');
}
```

**Note:** No custom `AetheriumError` class or Problem Details (RFC 7807) response format exists in this codebase. Error codes are simple string messages.

**No centralized error handling middleware** — each route handler has its own try/catch block.

---

## API Design Conventions (`server.ts`)

- Express server on port 3000
- Routes prefixed with `/api/`
- JSON request/response format exclusively
- Firestore direct integration (no ORM)
- Vite middleware for dev, static file serving for production
- No OpenAPI/Swagger documentation present
- No API version negotiation header — routes are simply `/api/health`, `/api/orders/:id`, etc.

**API Endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check |
| POST | `/api/webhook/whatsapp` | WhatsApp message ingestion |
| PATCH | `/api/orders/:id` | Human-in-the-loop order correction |
| POST | `/api/simulate` | Digital twin simulation run |
| GET | `/api/flows` | List workflow definitions |
| POST | `/api/flows` | Create workflow definition |

---

## TypeScript Patterns

**Interfaces vs Types:**
- **Interfaces used for:** Data models (`Order`, `Invoice`, `FlowDefinition`), Props (`HitlModalProps`), Error info (`FirestoreErrorInfo`)
- **Type aliases (inline or union) used for:** Literal unions like `'live' | 'offline'`, `'success' | 'info' | 'error'`, function signatures

**Type usage patterns:**
```typescript
// Literal unions for enum-like values
status: 'new' | 'confirmed' | 'cooking' | 'ready' | 'delivered' | 'cancelled';
payment_status: 'pending' | 'paid';

// Type assertions for Firestore snapshots
snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as Order));

// `any` used extensively for:
// - Firestore data return types (doc.data(), ...rest)
// - Component props (updates: any)
// - Generic object spreads
setEditedOrder({...editedOrder, customer_name: e.target.value});

// Optional properties with `?`
id?: string;
corrected_by?: string;
```

**Generics:**
- Minimal use — only observed in React hooks: `useState<Order[]>([])`, `useState<SimulationConfig>(...)`, `useState<'live' | 'offline'>('live')`

**Utility Types:**
- `Partial<PilotMetrics>` used in `Report` interface
- No mapped types, conditional types, or template literal types used

---

## Firebase Integration Patterns

- **Server-side:** Firebase Client SDK (not Admin SDK) used directly in `server.ts` for Firestore operations
- **Client-side:** Firebase Client SDK initialized in `src/lib/firebase-client.ts` with `experimentalForceLongPolling: true`
- **Firestore database ID** loaded from config JSON, not using the default database
- **Real-time listeners** via `onSnapshot()` with `query()` and `orderBy()`
- **Firestore operations:** `addDoc`, `collection`, `query`, `orderBy`, `onSnapshot`, `limit`, `doc`, `getDoc`, `updateDoc`, `getDocFromServer`
- **Authentication:** Firebase Auth via `getAuth(app)` — `auth.currentUser` used for error reporting context

---

## Styling Conventions

- **Utility-first CSS** with Tailwind CSS v4.1 (`@import "tailwindcss"`)
- **Custom theme:** Dark theme (`bg-[#050505]`, `text-[#E0E0E0]`), accent green (`#00FF9C`)
- **Font families:** Inter (sans-serif), JetBrains Mono (monospace) via Google Fonts
- **`cn()` utility** from `src/utils.ts` merges Tailwind classes using `clsx` + `tailwind-merge`
- **Dark mode only** — no light mode support
- **Inline `motion.div` animations** for micro-interactions (page transitions, progress bars, pulse effects)
- **ICU-like design language** with uppercase labels, monospace data, dotted borders, and telemetry-style toasts

```typescript
// cn() usage
className={cn(
  "text-[9px] font-bold uppercase",
  success ? "text-[#00FF9C]" : "text-red-500"
)}
```

---

## Project-Specific Conventions (Unique to CCAM)

**UI Design Language:**
- All UI text is **uppercase** with generous tracking (letter-spacing)
- Monospace font for data values and codes
- Dark backgrounds (`bg-[#0A0A0A]`, `bg-[#050505]`) with `border-[#222]` borders
- Accent color: `#00FF9C` (neon green) for active/highlight elements
- **"SYSTEM_TELEMETRY" style** notifications — toast messages resemble log entries with timestamps
- **Metrics displayed** as labeled KPI cards with percentage values and trends
- Sidebar navigation grouped by category (Insights, Governance, Operations, Automation)

**Notification/Toast Pattern:**
```typescript
const [notification, setNotification] = useState<{ message: string; type: 'success' | 'info' | 'error' } | null>(null);
// Auto-dismiss after 4 seconds
```

**Header Status Indicators:**
- Connection status badge: `SYNC_LIVE` (green) / `CONNECTION_OFFLINE` (red)
- Node identifier: `NODE: KUALA_LUMPUR_01`
- Console shortcut: `⌘K`

**Firebase AI Studio App:**
- Config loaded from `firebase-applet-config.json` (committed, contains API key — **not a secret in AI Studio context**)
- Environment variables: `GEMINI_API_KEY`, `APP_URL` (see `.env.example`)
- Deployed via AI Studio's Cloud Run integration (not a manual CI/CD pipeline)

---

## Git Conventions

- **No `.gitmessage` or commit convention config detected** — standard git usage
- **No branch naming conventions enforced** — no `develop`, `staging`, `main` branching strategy detected
- **Files tracked:** `.gitignore` excludes `node_modules/`, `build/`, `dist/`, `coverage/`, `.DS_Store`, `*.log`, `.env*` (except `.env.example`)
- **No husky/lint-staged configuration** — no pre-commit hooks

---

## What's NOT Present (Deliberate Omissions)

- ✅ No ESLint or Prettier configuration
- ✅ No test infrastructure (no jest, vitest, or test files)
- ✅ No CI/CD pipeline (no GitHub Actions, no `.github/` directory)
- ✅ No Storybook or component library documentation
- ✅ No CSS-in-JS or CSS modules — pure Tailwind
- ✅ No global state management (Redux, Zustand, Context)
- ✅ No routing library (React Router) — single-page app with tab-based navigation via `activeTab` state
- ✅ No API client library (no axios, no React Query) — raw `fetch()` calls
- ✅ No ORM — direct Firestore SDK calls

---

*Convention analysis: 2026-06-21*
