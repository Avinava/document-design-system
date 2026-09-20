# v2.0.0 isolates ingestion queues without changing producer payloads

**Release:** v2.0.0
**Date:** 2026-11-02
**Rollout:** Production

## Action required

No payload or authentication migration is required. Checkout, Catalog, and
Inventory must retain bounded retry behavior and verify `X-Request-Id`.

## What changed

- Added the stateless dispatcher.
- Replaced `ingest` with `ingest-a` and `ingest-b` plus split consumer groups.
- Added the read-only operator overview and producer blast-radius alerting.

## Compatibility and known issue

Lookup, warehouse schema, batch path, and 24-hour retention are unchanged. Shed
response is not announced until RAID-02 is approved. The original queue remains
available through 2026-11-20 for rollback.
