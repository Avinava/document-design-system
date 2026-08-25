# Cut over one partition at a time and keep the original queue recoverable

**Cutover:** 2026-11-02<br>
**Readiness gate:** 2026-10-28<br>
**Owner:** Platform

## Rehearsal and preconditions

The chaos environment is ready, producer fixtures pass, two skipped tests
execute, dashboards identify producer blast radius, and rollback is rehearsed.

## Cutover sequence

1. Begin dual-write in staging on 2026-10-12.
2. Shadow-read for one week and reconcile event IDs.
3. Route one partition to `ingest-a`; verify acceptance and warehouse rows.
4. Route the other partition to `ingest-b`; repeat verification.
5. Retain `ingest` until hypercare closes on 2026-11-20.

## Validation and rollback

No duplicate warehouse row, `POST /events` p99 below 200 ms, and lag falling
for ten minutes. Roll back routing to `ingest` on data mismatch, stalled lag,
or any crash loop. Never delete a queue during cutover or rollback.
