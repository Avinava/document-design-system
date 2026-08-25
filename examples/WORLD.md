# World — Northwind Ingestion

This is the fact ledger for every example in the repository: writing documents,
the report, figures, and the capacity deck. Writers may deepen an explanation,
but they must not create a second company, incident history, API contract, or
architecture.

## Product and reader context

**Northwind Ingestion** accepts events from first-party applications and partner
feeds, buffers them, and lands them in the warehouse used by analytics and
operations. It is an internal platform capability, not a customer-facing
product.

The Platform team operates the service. Checkout, Catalog, and Inventory are
producer teams. Reliability reviews failure behavior and alerting. Most readers
already understand HTTP, queues, containers, and warehouses; onboarding should
teach this system’s particular boundaries rather than basic software concepts.

## Current architecture

| Component | Current responsibility | Operational truth |
|---|---|---|
| Gateway | Authenticates producers and accepts `POST /events` | Returns `202` only after the event is accepted by the queue |
| Queue `ingest` | Buffers every first-party event | One queue, no failover, 24-hour retention |
| Consumer group | Validates and writes events to the warehouse | Three replicas normally; safe to add one at a time |
| Warehouse | Stores accepted events for downstream readers | Warehouse schema is outside RFC 014 |
| Batch path | Imports scheduled files | Separate from the HTTP path and outside RFC 014 |

The current runtime path is:

`producer → gateway → ingest → consumer group → warehouse`

The gateway and consumer run in the `ingest` namespace. Production uses the
`prod-ingest` cluster; staging uses `stage-ingest`. No example contains a real
hostname, credential, or account identifier.

## Proposed architecture — RFC 014

RFC 014 adds a stateless dispatcher after the gateway and replaces the single
queue with `ingest-a` and `ingest-b`. The dispatcher hashes the event ID and
routes even and odd partitions independently. Each queue receives its own
consumer group.

`producer → gateway → dispatcher → ingest-a|ingest-b → consumer group → warehouse`

The producer-facing path, authentication, payload, warehouse schema, batch path,
and 24-hour retention do not change.

The proposal requests two engineers for twelve weeks. The decision is needed by
2026-09-01. Dual-write begins in staging, followed by a one-week shadow read and
a controlled production cutover. The old queue remains available until the
shadow week closes.

## Stable API facts

| Item | Contract |
|---|---|
| Create | `POST /events` → `202` with `{"id","status"}` |
| Lookup | `GET /events/{id}` → `200` or `404` |
| Identity | Required opaque string field `id` |
| Correlation | Echo `X-Request-Id` on every response |
| Authentication | Service-to-service mTLS plus caller audience claim |
| Idempotency | Repeating an accepted event ID must not create a second warehouse row |
| Stable errors | `INGEST_SHED`, `INVALID_EVENT`, `UNAUTHORIZED_PRODUCER` |

The OpenAPI source remains `openapi/events.yaml`. Before RFC 014 ships, overload
returns `503`. The proposed behavior is `202` plus `INGEST_SHED` so producers can
retry with bounded backoff. That mismatch remains explicitly unresolved until
the API change is approved.

## Measurements and incident history

- Ingestion represents **41%** of the included platform footprint: 1.84M of
  2.50M units.
- **Four of the last six incidents** trace to the shared queue: 2026-03-14,
  2026-04-02, 2026-06-19, and 2026-07-30.
- Without a structural change, the observed cadence is roughly one halt per
  quarter.
- The 2026-07-30 incident lasted **1 hour 52 minutes**, from 14:12 to 16:04 UTC.
- Warehouse freshness peaked at **118 minutes**. Checkout, Catalog, and
  Inventory all returned `503` or blocked.
- Normal alerting pages after lag exceeds 120 seconds for five minutes. The
  corrective action changes that to 60 seconds and names the producer blast
  radius in the page.

## Test and release facts

Release candidate `sha-8132c3` was tested on 2026-08-12 in staging.

| Measure | Value |
|---|---:|
| Planned tests | 40 |
| Executed tests | 38 |
| Passed | 36 |
| Failed | 0 |
| Blocked | 0 |
| Skipped | 2 |

The two skipped tests require the two-queue chaos environment and therefore do
not run against the current single-queue build. The release verdict is
**go-with-waivers**, not an unconditional pass.

## Operator controls

- Dashboard: `Ingestion / lag`.
- Primary metric: `ingest_lag_seconds`.
- Current deployment: `ingest-consumer` in namespace `ingest`.
- Safe mitigation: add one consumer replica, observe lag for three minutes,
  and do not exceed six replicas without Reliability.
- Verification: lag falls for ten minutes and `POST /events` p99 stays below
  200 ms.
- Escalation: after 15 minutes without falling lag, or on any crash loop, page
  Platform primary and Reliability; stop changing replica counts.
- Never delete a queue as part of mitigation or rollback.

## Product surface used by design-handoff

The operator overview is a read-only page with a global status, one card per
queue, current lag, shed count, last event time, and a runbook link. States are
happy, idle, loading, partial data, error, and success after recovery. Status is
always written; color never carries it alone. The page refreshes every 15
seconds and supports keyboard navigation in document order.

## Evidence states

| Claim | State |
|---|---|
| Single queue, no failover | Verified from current configuration |
| 41% footprint concentration | Verified from the inventory snapshot |
| Four of six incidents share the coupling | Verified from incident tickets |
| Two independently recoverable queues reduce blast radius | Recommended by RFC 014 |
| Shed-and-alert rather than block | Unresolved; Reliability owns the decision |
| Rebalance under one failed queue | Unresolved until the chaos environment exists |
| Ingestion must degrade rather than fully stop | Provided by the Platform lead |

## People and ownership

- **Platform** owns the gateway, queue, consumers, RFC 014, and operator page.
- **Reliability** owns alert review and failure-behavior approval.
- **Checkout, Catalog, and Inventory** own producer retries and payload quality.
- The engineering handoff is from Platform to an **incoming owner**; examples do
  not use personal names.

## Theme use

Internal working documents use `field-notes` or `console-violet`. Leadership
proposals use `executive-navy`. Test, teaching, and design artifacts may use
`editorial-coral`. The `horizon` theme is the worked brand variant. A theme
changes voice; it never changes facts or document structure.

## Repository boundary

This repository is not Northwind. The examples pretend to live in a Northwind
repository under conventional paths such as `docs/adr/` and `docs/runbooks/`.
All commands, hostnames, keys, and paths are synthetic. Use
`api.example.invalid` and environment-variable placeholders; never add secrets.
