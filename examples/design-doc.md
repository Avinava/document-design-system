# Split ingestion so one queue cannot stop every producer

**Type:** Design document · RFC 014
**Status:** Proposed
**Decision by:** 2026-09-01
**Owner:** Platform
**Reviewers:** Reliability, Checkout, Catalog, Inventory

Introduce a stateless dispatcher and two independently recoverable queues while
keeping the producer API, event payload, retention, and warehouse unchanged.

> **The ask:** approve RFC 014: two Platform engineers for twelve weeks.
> **Decide by:** 2026-09-01. **Decider:** Platform director.
> **If declined:** keep the single queue and record it as an accepted risk.

## The recommendation

Route accepted events through a stateless dispatcher that hashes event ID to
`ingest-a` or `ingest-b`. Give each queue an independent consumer group and
recovery path.

Success means degradation, not invisibility. Losing one queue may reduce
throughput and require retries; it must not stop every producer.

## The shared queue is a platform-wide failure boundary

Ingestion holds 41% of the included platform footprint, or 1.84M of 2.50M
units. Four of the last six incidents began as queue backpressure and ended
with Checkout, Catalog, and Inventory unable to accept events.

Evidence: the inventory snapshot and incidents dated 2026-03-14, 2026-04-02,
2026-06-19, and 2026-07-30.

## Goals and boundaries

- Isolate a queue failure to roughly half the event partitions.
- Recover one path without redeploying producers or the other consumer group.
- Keep `POST /events`, authentication, payloads, retention, and warehouse
  schema stable.

Non-goals: replacing queue technology, redesigning the warehouse, changing the
batch path, or promising global event ordering.

## Proposed runtime path

`producer → gateway → dispatcher → ingest-a|ingest-b → consumer → warehouse`

The gateway authenticates and validates as it does today. The dispatcher is
stateless, hashes the opaque event ID, and writes to exactly one queue.

```yaml
dispatcher:
  partition_key: event.id
  routes: [ingest-a, ingest-b]
  on_queue_unavailable: shed_and_alert
  max_gateway_wait_ms: 200
```

## Options considered on the same criteria

| Option | Isolation | Operational cost | Decision |
|---|---|---|---|
| Keep one queue | None | Lowest | Reject: preserves the quarterly halt |
| Larger queue | None | Low | Reject: changes when saturation arrives |
| Two partitioned queues | Strong | Bounded | **Recommend** |
| Queue per producer | Strongest | High | Reject for current producer count |

## Rollout and rollback

1. Build the dispatcher and deterministic partition tests.
2. Dual-write in staging and shadow-read both new queues for one week.
3. Run the one-queue-down chaos test.
4. Cut production reads behind a flag and retain the original queue through
   the observation week.

Rollback flips reads and writes back to `ingest`. It never deletes queues or
mutates warehouse data.

## Decision needed

Approve two Platform engineers for twelve weeks. The catalog backfill slips one
quarter. Before build, Reliability owns the shed-versus-block decision and
Platform owns partial-failure rebalance proof.

Without approval, keep the current queue and record that as an accepted risk.
