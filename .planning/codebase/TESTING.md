# Testing Patterns

**Analysis Date:** 2026-06-21

**Project:** CCAM (Contextual Conversational Automation Mesh) — Firebase AI Studio applet

---

## Current Testing Status

**No test infrastructure exists in this repository.** The codebase has:

- ❌ No test framework (no jest, vitest, mocha, or any test runner)
- ❌ No test configuration files (`jest.config.*`, `vitest.config.*`, `.mocharc.*`)
- ❌ No test files (no `*.test.*`, `*.spec.*`, `__tests__/` directories)
- ❌ No test scripts in `package.json`
- ❌ No coverage configuration
- ❌ No CI/CD pipeline or GitHub Actions workflows
- ❌ No mocking libraries
- ❌ No test fixtures or factories
- ❌ No `.husky/` or pre-commit hooks

The only "testing" present is the TypeScript compiler type-check via `"lint": "tsc --noEmit"`.

---

## Recommended Test Infrastructure

Based on the project's technology stack (TypeScript, React 19, Vite 6, Express 4, Firebase), the following test infrastructure is recommended:

### Unit & Integration Tests

**Recommended Runner:** Vitest (native Vite integration, same config as build)

**Installation:**
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

**Configuration:** Add to `vite.config.ts` or create `vitest.config.ts`:
```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        branches: 60,
        functions: 70,
        lines: 70,
        statements: 70,
      },
    },
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, '.') },
  },
});
```

**Test setup file (`src/test/setup.ts`):**
```typescript
import '@testing-library/jest-dom';
```

### E2E Tests

**Recommended Runner:** Playwright or Cypress

**Installation (Playwright):**
```bash
npm install -D @playwright/test
npx playwright install
```

### Package.json Scripts

Add to `package.json`:
```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "npx playwright test"
  }
}
```

---

## Test File Organization (Recommended)

```
src/
├── test/
│   ├── setup.ts              # Global test setup
│   ├── fixtures/             # Test data factories
│   │   ├── orders.ts
│   │   ├── invoices.ts
│   │   └── flows.ts
│   ├── mocks/                # Mock implementations
│   │   ├── firebase.ts       # Mock Firestore
│   │   └── gemini.ts         # Mock Gemini API
│   └── helpers/              # Test utilities
│       └── render.tsx        # Custom render with providers
├── components/               # Co-located component tests
│   ├── DashboardView.test.tsx
│   ├── OrdersView.test.tsx
│   └── ...
├── lib/
│   ├── gemini.test.ts
│   └── firebase-client.test.ts
```

**Naming convention (recommended):**
- `*.test.ts` for utility/lib unit tests
- `*.test.tsx` for component tests
- `*.e2e.ts` for end-to-end tests
- Co-locate tests next to source files (preferred) or in `__tests__/` directories

---

## What Should Be Tested

### Critical Test Areas

**1. Gemini AI Parser (`src/lib/gemini.ts`):**
- `parseWhatsAppMessage()` returns correct JSON structure
- Falls back gracefully on API errors
- Handles markdown-formatted JSON responses
- Handles empty/null/edge-case messages

**2. API Routes (`server.ts`):**
- `GET /api/health` returns `{ status: "ok" }`
- `POST /api/webhook/whatsapp` validates message body (400 on missing message)
- `POST /api/webhook/whatsapp` creates Firestore records
- `PATCH /api/orders/:id` updates order and generates invoice on status change
- `POST /api/simulate` returns simulation results
- `GET /api/flows` / `POST /api/flows` CRUD operations

**3. Firebase Client (`src/lib/firebase-client.ts`):**
- Firebase app initializes with config
- Firestore instance is created with correct database ID
- Auth instance is created

**4. Components (Firestore-dependent):**
- `OrdersView` renders loading/empty/data states
- `FinancialsView` handles snapshot subscription lifecycle
- `SimulatorView` triggers API call on button click
- `HitlModal` renders correct order data and supports editing
- `CommandPalette` filters commands and navigates on select

**5. Utility functions (`src/utils.ts`, `src/types.ts`):**
- `cn()` merges class names correctly
- `handleFirestoreError()` formats error info correctly

---

## Mocking Strategy (Recommended)

### Mocking Firebase
Since Firebase Firestore is used extensively in components, a mock strategy is needed:

```typescript
// src/test/mocks/firebase.ts
export const mockCollection = vi.fn();
export const mockQuery = vi.fn();
export const mockOnSnapshot = vi.fn((_q, callback) => {
  callback({
    docs: [],
    metadata: { hasPendingWrites: false }
  });
  return vi.fn(); // unsubscribe
});

vi.mock('firebase/firestore', () => ({
  collection: mockCollection,
  query: mockQuery,
  onSnapshot: mockOnSnapshot,
  addDoc: vi.fn(),
  doc: vi.fn(),
  getDoc: vi.fn(),
  updateDoc: vi.fn(),
  getDocFromServer: vi.fn(),
  orderBy: vi.fn(),
  limit: vi.fn(),
  serverTimestamp: vi.fn(() => new Date()),
}));
```

### Mocking Gemini API
```typescript
// src/test/mocks/gemini.ts
export const mockParseWhatsAppMessage = vi.fn();
vi.mock('../lib/gemini', () => ({
  parseWhatsAppMessage: mockParseWhatsAppMessage,
}));
```

### Mocking Server API calls
For component tests that call `fetch()`, use `vi.fn()` with MSW (Mock Service Worker) or simple `vi.spyOn(global, 'fetch')`.

---

## Component Test Patterns (Recommended)

```typescript
// src/components/OrdersView.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import OrdersView from './OrdersView';

// Mock firebase
vi.mock('firebase/firestore', () => ({
  collection: vi.fn(() => 'orders'),
  query: vi.fn(),
  onSnapshot: vi.fn((_q, cb) => {
    cb({
      docs: [
        { id: '1', data: () => ({ customer_name: 'Test', confidence: 0.95, items: [], status: 'confirmed' }) }
      ]
    });
    return vi.fn();
  }),
  orderBy: vi.fn(),
  limit: vi.fn(),
}));

describe('OrdersView', () => {
  it('renders the order buffer section', async () => {
    render(<OrdersView onCorrect={vi.fn()} />);
    expect(screen.getByText('Order Buffer')).toBeInTheDocument();
  });
});
```

---

## Integration Test Patterns (Recommended)

For testing the Express server:

```typescript
// server.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import http from 'http';

describe('API Server', () => {
  it('GET /api/health returns ok', async () => {
    const res = await fetch('http://localhost:3000/api/health');
    const data = await res.json();
    expect(res.status).toBe(200);
    expect(data.status).toBe('ok');
  });

  it('POST /api/webhook/whatsapp returns 400 without message', async () => {
    const res = await fetch('http://localhost:3000/api/webhook/whatsapp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.error).toBe('Message is required');
  });
});
```

---

## Run Commands (Recommended)

```bash
npm run test              # Run all tests (single run)
npm run test:watch        # Watch mode for development
npm run test:coverage     # Run with coverage report
npm run test:e2e          # Run end-to-end tests
npx vitest run --reporter=verbose   # Verbose output
```

---

## Coverage Targets (Recommended)

| Metric | Target |
|--------|--------|
| Statements | ≥ 70% |
| Branches | ≥ 60% |
| Functions | ≥ 70% |
| Lines | ≥ 70% |

Given the current state of zero tests, focus on:

1. **Phase 1** (initial sprint): Cover utility functions, API health endpoint, and Gemini parser
2. **Phase 2** (core coverage): Cover all API routes with integration tests
3. **Phase 3** (component tests): Cover key views with Firestore mock
4. **Phase 4** (E2E): Cover critical user flows (ingestion → confirmation → invoice)

---

## CI/CD Pipeline (Recommended)

**No CI/CD infrastructure currently exists.** Recommended GitHub Actions workflow (`.github/workflows/test.yml`):

```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run test -- --coverage
      - uses: codecov/codecov-action@v4
```

---

## Current Commands (from `package.json`)

```bash
npm run dev      # Start dev server (tsx server.ts)
npm run build    # Build frontend + server
npm run start    # Start production server
npm run clean    # Remove dist/
npm run lint     # TypeScript type-check only
```

---

## Gaps & Risks

| Gap | Impact | Risk Level |
|-----|--------|------------|
| No unit tests for Gemini parser | Production parser failures go undetected | High |
| No API integration tests | API contract breaks are silent | High |
| No component tests | UI regressions from prop/state changes | Medium |
| No type-checking on CI | Type errors can be merged | Medium |
| No E2E tests | Critical user flows can break | High |
| No coverage thresholds | No quality gate for contributions | Medium |

---

*Testing analysis: 2026-06-21*
