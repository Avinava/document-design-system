# Quality evidence follows the failure risks, not the component list

**Release:** v2.0.0
**Readiness:** 2026-10-28
**Environment:** staging and two-queue chaos

## Quality risks

The release must prove independent queue recovery, stable idempotency, unchanged
producer behavior, bounded retry, correct partitioning, and reversible cutover.

## Test levels and evidence

| Level | Evidence | Owner |
|---|---|---|
| Contract | API and error behavior | Platform |
| Component | Dispatcher partition and consumer writes | Platform |
| Chaos | One queue down without cross-partition stop | Reliability |
| Producer | Checkout, Catalog, Inventory retries | Producer teams |
| Cutover | Reconciliation and rollback rehearsal | Platform |

## Entry and exit

Entry requires the chaos environment by 2026-09-18. Exit requires REQ-101
through REQ-105 evidence, zero release-blocking defects, executed chaos cases,
and accepted residual risk. Results belong in the named `test-report`.
