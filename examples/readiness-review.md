# v2.0.0 is not ready until chaos and rollback evidence close

**Verdict:** Conditional go<br>
**Review:** 2026-10-28<br>
**Release:** 2026-11-02

## Verdict

Proceed only if one failed queue leaves the other accepting events, dashboards
name producer blast radius, rollback is rehearsed, and the two skipped chaos
tests execute.

## Criteria

| Area | State | Evidence or gap |
|---|---|---|
| Ownership and support | Ready | Platform and Reliability model agreed |
| Contract compatibility | Ready | Payload and authentication unchanged |
| Observability | Conditional | Blast-radius dashboard proof required |
| Failure isolation | Blocking | Two-queue chaos cases not yet executed |
| Rollback | Conditional | Production-like rehearsal required |
| Producer validation | Conditional | Fixtures due 2026-10-16 |

No checkbox substitutes for linked evidence. Any waiver names an owner and
expiry; a blocking criterion moves 2026-11-02.
