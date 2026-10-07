---
type: custom
title: Northwind Ingestion for engineers who know batch
pattern: learning
modules: [scope-strip, learning-goal, section-num, reading-time, figure, system-map, crosswalk, table-scroll, specimen, takeaway]
nearest-type: explanation
---

# Northwind Ingestion for engineers who know batch

**Type:** custom, composed from the `learning` pattern (nearest type: explanation)

You already know how scheduled loads land in a warehouse. This primer maps that
knowledge onto a path that never waits for a window: what carries over, what
bends, and the two habits that break here.

| For | Read time | Read with | This is not |
|---|---|---|---|
| Engineers joining Platform from the batch and warehouse side | 25 min, five sections, no setup | [Onboarding](onboarding.md) to run it, [the explanation](explanation.md) for why it halts, [the runbook](runbook.md) when lag rises | A setup checklist, an operating procedure, or the RFC 014 decision |

**Learning goal.** By the end, you can:

- trace one event from producer to warehouse and name who owns each hop;
- say which batch habits carry over, which bend, and which break on this path;
- read lag the way Platform does, and know when to stop changing replicas.

## The path is pushed, not pulled

_Reading time: 5 min._

In a batch pipeline, the warehouse side decides when data moves: a schedule
fires, a job reads files, a load commits. Here the producers decide. Checkout,
Catalog, and Inventory send each event over HTTP the moment it happens, and
every hop after that runs continuously.

`producer → gateway → ingest → consumer group → warehouse`

![Current runtime path. The queue is the only component without a failover.](platform-architecture.svg)

Platform owns the gateway, the `ingest` queue, and the consumers. Producer
teams own their retries and payload quality. Both the gateway and the consumers
run in the `ingest` namespace, on `prod-ingest` in production and
`stage-ingest` in staging.

**Section takeaway:** nothing on this path runs on a timer. Work arrives when
producers send it, so capacity problems show up as waiting, not as a late job.

## What carries over from batch, and what breaks

_Reading time: 8 min._

Most of your warehouse knowledge still applies once an event is in the consumer
group. The surprises are upstream of it, where batch thinking assumes a window
and a job boundary that this path does not have.

| In batch | Here | Fit | What to adjust |
|---|---|---|---|
| Target table | Warehouse | Holds | The same warehouse analytics and operations read. Its schema is outside RFC 014. |
| Loader job | Consumer group, three replicas | Holds | Validates and writes events to the warehouse. Scale it one replica at a time. |
| Landing area | Queue `ingest` | Partial | Holds work between arrival and load, but it is shared by every producer, has no failover, and keeps events for 24 hours. |
| Rerun | Retry with the same event ID | Partial | Producers retry single events. Repeating an accepted ID must not create a second warehouse row; a new ID makes a second event. |
| Freshness check | Lag, `ingest_lag_seconds` | Partial | Freshness is how far consumers trail arrivals, not whether a job finished. |
| Schedule | None on this path | Breaks | Nothing waits for a trigger. Scheduled file imports still exist, on the separate batch path. |
| Load window | `202` at the gateway | Breaks | There is no window to finish inside. The gateway answers each event as soon as the queue accepts it. |
| Failed run | Shared-queue halt | Breaks | A failed batch run stops its own load. A full queue stops Checkout, Catalog, and Inventory together. |

Holds: your intuition is right. Partial: right shape, different limits.
Breaks: unlearn it here.

**Section takeaway:** trust your instincts from the consumer group onward.
Upstream of it, replace “window” with “acceptance” and “failed job” with
“shared halt”.

## Acceptance is not arrival

_Reading time: 4 min._

A batch load is done when the rows are in the table. Here, the gateway's answer
comes much earlier: it returns `202` only after the queue has accepted the
event, and the warehouse write happens later, in the consumer group.

```http
POST /events
X-Request-Id: req_7f3

{"id":"evt_01","type":"checkout.paid"}

202 {"id":"evt_01","status":"accepted"}
```

The event ID is the retry anchor; the request ID is echoed on every response
for tracing.

**Section takeaway:** `202` means queued, not warehoused. When you reason about
a missing row, start from lag, not from the gateway.

## Freshness is lag, and lag has one safe response

_Reading time: 5 min._

Platform watches `ingest_lag_seconds` on the `Ingestion / lag` dashboard.
Normal alerting pages after lag exceeds 120 seconds for five minutes; the
corrective action from the 2026-07-30 incident changes that to 60 seconds and
names the producer blast radius in the page.

That incident lasted 1 hour 52 minutes, and warehouse freshness peaked at 118
minutes. The safe mitigation is the one the runbook prescribes: add one
consumer replica, observe lag for three minutes, and do not exceed six replicas
without Reliability.

**Section takeaway:** lag is your freshness signal. The safe response is one
replica at a time, and a queue is never deleted as mitigation or rollback.

## What changes next, and what this primer leaves out

_Reading time: 3 min._

RFC 014 proposes a stateless dispatcher after the gateway that splits traffic
across `ingest-a` and `ingest-b`, each with its own consumer group. The
producer-facing path, the warehouse schema, the batch path, and 24-hour
retention do not change. Until it is approved, treat it as proposed, not
current.

Not covered here, because the platform's fact ledger does not settle them: how
the batch path's schedules are owned, bulk backfill into the warehouse, and the
warehouse schema itself. Ask Platform before assuming any of them behave like
the event path.

**Section takeaway:** you now have the model. Run it with the onboarding, and
keep the runbook open the first time lag rises.
