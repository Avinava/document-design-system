# The queue is the failure boundary; faster detection alone will not fix it

**Type:** Discovery brief · DISC-012
**Window:** 2026-07-01–2026-08-18
**Decision enabled:** go / stop / reframe RFC 014
**Owner:** Platform

Incident evidence supports changing the architecture. A one-queue-down test is
the fastest way to validate the split before funding the full build.

## Question and method

Is the right investment a queue split, better detection, more consumer
capacity, or a producer-side change?

We reviewed six incidents, the inventory snapshot, gateway and queue telemetry,
the current runbook, and interviews with the three producer teams and
Reliability.

## Evidence converges on one shared boundary

- Four of six incidents follow the same backpressure-to-gateway chain.
- Checkout dominates volume, but all three producers fail together.
- Consumer scaling restores service and has not prevented recurrence.
- Producers can retry, but the API has no bounded shed signal today.

## Opportunities ranked by learning value

| Opportunity | Learning value | Recommendation |
|---|---|---|
| One-queue-down prototype | Tests the architectural claim | **Test first** |
| Earlier alert with blast radius | Improves response, not isolation | Do regardless |
| More default consumers | Adds buffer, retains coupling | Insufficient |
| Producer-specific queues | Strong isolation, high cost | Too broad |

## Constraints and unresolved assumptions

- The producer API and warehouse schema must remain stable.
- Reliability has not approved shed-and-alert behavior.
- Consumer rebalance under one failed queue is not observed.
- Ordering is not guaranteed today and should not enter indirectly.

## Recommendation

Build the dispatcher and two staging queues, then fail one queue deliberately.

- **Go** if the healthy queue continues below 200 ms gateway p99.
- **Reframe** if rebalance couples both queues or wait cannot be bounded.
- **Stop** if isolation requires a producer or warehouse contract change.
