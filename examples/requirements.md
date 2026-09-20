# Ingestion must isolate queue failure without changing producer behavior

**Status:** Proposed
**Scope:** RFC 014
**Decision by:** 2026-09-01

## Outcome and boundary

Checkout, Catalog, and Inventory must continue accepting events when one queue
is unavailable. Payload, authentication, lookup, warehouse schema, batch path,
and 24-hour retention remain unchanged.

## Requirements

- **REQ-101:** `POST /events` must return `202` only after one queue accepts the event.
- **REQ-102:** A failed queue must not prevent the other queue from accepting events.
- **REQ-103:** Repeating an accepted event ID must not create a second warehouse row.
- **REQ-104:** Every response must echo `X-Request-Id`.
- **REQ-105:** Rollback must restore the original queue without data repair.

## Acceptance and traceability

The 2026-10-28 readiness review links each requirement to automated or chaos
evidence. Shed response remains unresolved under RAID-02.
