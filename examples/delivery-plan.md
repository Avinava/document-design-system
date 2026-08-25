# Five gates carry RFC 014 from decision to handoff

**Baseline:** 24 engineer-weeks<br>
**Window:** 2026-08-31–2026-11-20<br>
**Status:** Amber — decision and environment dependency

## Milestones

1. Design accepted — 2026-09-01.
2. Chaos environment ready — 2026-09-18.
3. Staging dual-write — 2026-10-12.
4. Readiness decision — 2026-10-28.
5. Production and handoff — 2026-11-02 to 2026-11-20.

## Workstreams and dependencies

Platform owns runtime and operator work. Reliability owns failure-behavior
approval. Checkout, Catalog, and Inventory own retry fixtures by 2026-10-16.
RAID-01 is the critical dependency; CR-003 is outside the baseline.

## Governance

Weekly status updates forecast gates. Scope or effort movement uses a change
request. A missed readiness criterion moves the release rather than being
reported as complete.
