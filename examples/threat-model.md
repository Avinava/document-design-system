# Split ingestion reduces blast radius but does not settle overload behavior

**Status:** Review required<br>
**Scope:** RFC 014<br>
**Review gate:** 2026-10-28

## Assurance position

Conditional: the design improves availability isolation, but RAID-02 must settle
the shed response before release communication.

## System and trust boundaries

Producers authenticate with mTLS and an audience claim. The gateway accepts
events, the dispatcher partitions by ID, queues isolate work, consumers write
to the warehouse, and the operator overview is read-only.

## Threats and treatment

| ID | Threat | Existing or planned control | Residual state |
|---|---|---|---|
| THR-01 | Forged caller audience | mTLS plus audience claim | Validate negative cases |
| THR-02 | Replayed event ID | Idempotent warehouse write | Test across both queues |
| THR-03 | Queue-flood denial of service | Bounded shedding and isolation | RAID-02 unresolved |
| THR-04 | Operator metadata exposure | Read-only, least-privilege access | Review before go-live |

Reliability accepts residual availability risk; Platform owns evidence.
