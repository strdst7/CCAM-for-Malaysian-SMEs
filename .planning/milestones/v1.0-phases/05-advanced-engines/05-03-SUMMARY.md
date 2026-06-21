---
phase: 05-advanced-engines
plan: 03
subsystem: [procurement-engine, notification-engine]
tags: [procurement, purchase-order, supplier-adapter, reportlab, sendgrid, notification, email, in-app, routing]
requires: []
provides:
  - Standalone procurement engine package (ccam-procurement) with pluggable supplier adapters and PO generation
  - Standalone notification engine package (ccam-notification) with multi-channel routing
affects:
  - Plan 04: Backend API wiring — procurement endpoints, notification API
tech-stack:
  added:
    - reportlab>=4.2.0 (PDF generation for purchase orders)
    - sendgrid>=6.11.0 (Email delivery for PO and notifications)
  patterns:
    - Standalone package under engines/ with pyproject.toml, src/ layout, hatchling build
    - Pluggable adapter pattern via ABC (SupplierAdapter) with 4 abstract methods
    - Multi-channel notification routing with template system
    - SendGrid primary, SMTP fallback for email delivery
    - Python string.Template for notification template rendering
key-files:
  created:
    - engines/procurement/pyproject.toml — Package definition with reportlab, sendgrid deps
    - engines/procurement/src/ccam_procurement/__init__.py — Public API exports
    - engines/procurement/src/ccam_procurement/models.py — PurchaseOrder, POLineItem, POStatus, SupplierContact, POGenerateRequest
    - engines/procurement/src/ccam_procurement/supplier_abc.py — SupplierAdapter ABC with order_ingredients, generate_po, send_po, track_status (D-14)
    - engines/procurement/src/ccam_procurement/po_generator.py — PDF PO generation via reportlab, SimplePOGenerator for text output
    - engines/procurement/src/ccam_procurement/email_adapter.py — EmailSupplierAdapter: SendGrid primary, SMTP fallback (D-15)
    - engines/procurement/src/ccam_procurement/engine.py — ProcurementEngine orchestrating PO creation, generation, delivery
    - engines/procurement/src/ccam_procurement/exceptions.py — ProcurementError, AdapterError, POGenerationError, SupplierNotFoundError
    - engines/notification/pyproject.toml — Package definition with sendgrid dep
    - engines/notification/src/ccam_notification/__init__.py — Public API exports
    - engines/notification/src/ccam_notification/models.py — Notification, NotificationTemplate, SendResult, channel/priority/status enums
    - engines/notification/src/ccam_notification/email_channel.py — EmailChannel: SendGrid primary, SMTP fallback
    - engines/notification/src/ccam_notification/inapp_channel.py — InAppChannel: in-memory store, retrieval, mark_read, count_unread (D-17)
    - engines/notification/src/ccam_notification/router.py — NotificationRouter: multi-channel dispatch with template registration
    - engines/notification/src/ccam_notification/engine.py — NotificationEngine with notify/notify_email/notify_inapp convenience methods
    - engines/notification/src/ccam_notification/exceptions.py — NotificationError, ChannelError, TemplateError, DeliveryError
    - engines/procurement/src/ccam_procurement/__init__.py
  decision_refs:
    - D-14: Pluggable supplier adapters via ABC
    - D-15: v1 ships email-based PO delivery
    - D-16: Standardized PO template format
    - D-17: v1 ships email + in-app notification channels
    - D-18: WhatsApp/push notifications deferred post-v1
requirements: [ENG-04, ENG-05]
metrics:
  duration: ~4 minutes
  files_created: 16
  commits: 2
---

# Phase 5 Plan 3: Procurement Engine & Notification Engine Summary

Build the Procurement Engine (ENG-04) and Notification Engine (ENG-05) as standalone Python packages under `engines/`. These engines provide pluggable supplier adapters with PDF purchase order delivery and multi-channel notification routing.

## What Was Built

### Procurement Engine (engines/procurement/)

The `ccam_procurement` package implements full purchase order lifecycle:

1. **SupplierAdapter ABC** — Abstract base class defining the 4-method interface: `order_ingredients()`, `generate_po()`, `send_po()`, `track_status()` (D-14). All supplier-specific implementations must subclass this.

2. **POGenerator + SimplePOGenerator** — PDF generation via reportlab with professional PO layout (header, line items table with headers/totals/notes). `SimplePOGenerator` provides a plain-text alternative.

3. **EmailSupplierAdapter** — v1's sole concrete adapter (D-15). Sends PDF POs via SendGrid API (primary) with SMTP fallback. Supplier contact info comes from `SupplierContact` object.

4. **ProcurementEngine** — High-level orchestrator. Creates `PurchaseOrder` from `POGenerateRequest`, optionally registers custom adapters per supplier, auto-creates email adapter as default, generates PDF, delivers, and returns PO with updated status.

### Notification Engine (engines/notification/)

The `ccam_notification` package implements multi-channel notification delivery (D-17):

1. **EmailChannel** — Email delivery via SendGrid (primary) with SMTP fallback. Uses Python `string.Template` for subject/body rendering.

2. **InAppChannel** — In-memory notification store supporting `send()`, `get_notifications()`, `mark_read()`, `count_unread()`. Designed for SSE or polling delivery; backend persistence added in Plan 04.

3. **NotificationRouter** — Multi-channel dispatcher with template registration. Resolves templates by key, falls back to default templates (`${title}` / `${body}`). Routes to EmailChannel or InAppChannel based on `NotificationChannel` enum.

4. **NotificationEngine** — Top-level API with `notify()`, `notify_email()`, `notify_inapp()` convenience methods.

### Design Decisions Applied

| Decision | Implementation |
|----------|---------------|
| D-14 | SupplierAdapter ABC with 4 abstract methods |
| D-15 | EmailSupplierAdapter: SendGrid primary, SMTP fallback |
| D-16 | POGenerator creates standardized PDF PO documents |
| D-17 | EmailChannel + InAppChannel deployed; WhatsApp/push deferred |
| D-18 | No WhatsApp Business API or FCM in v1 |
| D-19 | Procurement changes are advisory only |

## Verification Results

### Procurement Engine (Task 1)
- ✅ PO model works (total=RM600.00)
- ✅ PDF generated (2214 bytes) via reportlab
- ✅ Simple PO text generated
- ✅ SupplierAdapter ABC defines 4 abstract methods
- ✅ PO creation attempted (delivery expected to fail in dev without SMTP/SendGrid)

### Notification Engine (Task 2)
- ✅ Notification model works
- ✅ In-app notification stored and retrievable
- ✅ Mark read updates unread count correctly
- ✅ Router dispatches to correct channel with registered templates
- ✅ NotificationEngine.notify_inapp() end-to-end
- ✅ EmailChannel constructable

## Commits

| Hash | Message |
|------|---------|
| `71bba7a` | `feat(05-advanced-engines): add procurement engine — supplier ABC, PO generation, email adapter` |
| `3aa8f74` | `feat(05-advanced-engines): add notification engine — email channel, in-app channel, router` |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Verification script template registration**
- **Found during:** Task 2 verification
- **Issue:** The plan's verification script created a Notification with `template_key='order_confirmation'` but did not register a matching template before calling `router.send()`, causing a `TemplateError`.
- **Fix:** Registered the template via `router.register_template()` before sending in the verification step.
- **Impact:** No code changes needed — only the inline verification command was adjusted. The router's strict template enforcement is correct behavior.

## Known Stubs

None. Both engines are fully functional within their v1 scope.

## Threat Flags

None. The STRIDE mitigations from the plan's threat model are respected:
- T-05-09 (Spoofing): Accepted — notifications are informational, not auth
- T-05-10 (Tampering — PDF): Mitigated — reportlab trusted, structured dataclass input
- T-05-11 (Info disclosure — email): Mitigated — TLS by default
- T-05-12 (Tampering — supplier adapter): Accepted — v1 advisory POs only

## Self-Check: PASSED
- All 16 source files verified on disk
- Both commits verified in git log
- Both packages install cleanly via pip/uv
- All verification assertions pass
- No accidental file deletions in commits
