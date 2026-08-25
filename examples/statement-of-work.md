# Deliver the split ingestion path through controlled handoff

**Status:** Draft<br>
**Window:** 2026-08-31–2026-11-20<br>
**Effort cap:** 24 engineer-weeks

## Objective and services

Design, build, verify, release, and hand over RFC 014. Services cover the
dispatcher, two queues and consumer groups, observability, operator overview,
chaos evidence, cutover, runbooks, and handoff.

## Deliverables and acceptance

| Deliverable | Acceptance owner | Gate |
|---|---|---|
| Design and requirements | Platform director | 2026-09-01 |
| Staging path and chaos evidence | Reliability | 2026-10-28 |
| v2.0.0 and support material | Platform | 2026-11-20 |

## Responsibilities and exclusions

Platform supplies delivery capacity; Reliability approves failure behavior;
producer teams supply retry fixtures. Payload, authentication, warehouse schema,
batch path, retention, rates, payment terms, and legal clauses are excluded.

Changes use the approved change-request process; CR-003 is not included.
