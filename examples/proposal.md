# Two engineers for one quarter to remove the shared ingestion failure

**Type:** Investment proposal
**Asked of:** Platform director
**Decision by:** 2026-09-01
**Author:** Platform

Approve RFC 014 now so the next queue failure degrades throughput instead of
stopping Checkout, Catalog, and Inventory together.

## Why fund this now

Four of the last six incidents ended in the same platform-wide halt. Ingestion
represents 41% of the measured footprint, and the observed cadence is roughly
one repeat per quarter if the boundary does not change.

## What the quarter buys

- A stateless dispatcher that partitions accepted events by event ID.
- Two queues and consumer groups that deploy and recover independently.
- Dashboards, alerting, runbooks, and a one-queue-down chaos test.
- A reversible production cutover with the original queue retained.

## Cost and opportunity cost

Two engineers for twelve weeks, plus Reliability review during the game day and
cutover. The catalog backfill slips one quarter. Ongoing cost is one additional
queue, consumer group, and dashboard lane.

## The alternatives preserve the failure mode

| Option | This quarter | Failure boundary | Decision |
|---|---|---|---|
| Do nothing | No delivery cost | Shared | Reject |
| Increase capacity | Lower cost | Shared | Reject |
| Split the path | Staffed quarter | Independent partitions | **Recommend** |
| Queue per producer | Larger build | Independent producers | Too broad |

## The ask

Fund two Platform engineers from 2026-09-07 through 2026-11-27. Release only
when one failed queue cannot stall the other and rollback returns traffic to
`ingest` without data repair.

If declined, record the current single queue as an accepted risk and keep the
60-second alert action.
