# Split ingestion without changing the producer contract

**Status:** Proposed
**Window:** 2026-08-31–2026-11-20
**Sponsor:** Platform director
**Delivery owner:** Platform

## Purpose and outcomes

Deliver RFC 014 so one queue failure cannot stop every producer. Success means
one failed queue leaves the other accepting events, rollback is rehearsed, and
the producer API and warehouse schema do not change.

## Scope fence

In scope: dispatcher, two queues and consumer groups, operator overview,
chaos evidence, runbooks, release, and handoff. Out: payload, authentication,
warehouse schema, batch path, and retention.

## Governance and gates

Platform delivers; Reliability approves failure behavior; producer teams prove
retries. Gates are design on 2026-09-01, readiness on 2026-10-28, release on
2026-11-02, and handoff on 2026-11-20.

## Initial exposure

RAID-01 and RAID-02 are high. Scope, time, or effort changes require an approved
change request; CR-003 is not part of the baseline.
