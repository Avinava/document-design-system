# Dispatcher routing and failure behavior

**Type:** Normative specification · SPEC-014
**Status:** Proposed
**Owner:** Platform
**Companion:** RFC 014

This specification defines how an accepted event is assigned to one queue, how
quickly the gateway must return, and what implementations must prove.

The keywords MUST, SHOULD, and MAY are normative.

## Scope

The contract begins after the gateway accepts and validates `POST /events`. It
ends when the dispatcher writes to `ingest-a` or `ingest-b`, or records a
bounded shed result.

Authentication, payload schema, warehouse writes, batch ingestion, and global
ordering are outside this specification.

## Definitions

- **Accepted event:** caller, envelope, and required fields passed validation.
- **Partition:** `hash(event.id) mod 2`; even routes to A, odd to B.
- **Shed:** bounded refusal to enqueue on an unavailable selected queue.
- **Healthy path:** selected queue and consumer group are available.

## Normative requirements

- **REQ-001 — Exactly one destination.** Every accepted event MUST be assigned
  to exactly one queue.
- **REQ-002 — Deterministic partition.** Assignment MUST be a function of event
  ID alone and remain stable across retries.
- **REQ-003 — Bounded gateway wait.** A selected queue failure MUST NOT hold the
  gateway request longer than 200 ms.
- **REQ-004 — No payload persistence.** The dispatcher MUST NOT inspect domain
  fields or persist event bodies.
- **REQ-005 — Observable outcome.** Every enqueue or shed MUST increment the
  matching partition counter and retain request ID.
- **REQ-006 — Independent health.** Failure of one queue MUST NOT prevent writes
  to the other queue.

## Worked examples

```text
event.id = "evt_01"
hash(event.id) mod 2 = 0
destination = ingest-a
result = enqueued
```

```text
event.id = "evt_02"
destination = ingest-b
ingest-b = unavailable
gateway wait = 187 ms
result = INGEST_SHED
```

## Compliance matrix

| Requirement | Evidence | Gate |
|---|---|---|
| REQ-001–002 | Fixed-vector test across 10,000 IDs and retries | Stable assignments |
| REQ-003 | Selected queue unavailable under load | p99 below 200 ms |
| REQ-004 | Code review and storage inventory | No body access or store |
| REQ-005 | Dashboard and trace fixture | Every outcome correlated |
| REQ-006 | One-queue-down chaos test | Healthy path continues |
