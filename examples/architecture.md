# One producer-facing gateway, one shared queue, one warehouse landing path

**Type:** Current-state architecture · Northwind Ingestion
**As of:** 2026-08-18
**Owner:** Platform
**Scope:** HTTP acceptance through warehouse write
**Change proposal:** RFC 014

This page describes production as it exists. The dispatcher and split queues
are proposed, not current.

## System context and boundary

Checkout, Catalog, and Inventory are first-party producers. The gateway
authenticates and accepts events. The warehouse and its readers are downstream.
Batch imports are separate and out of scope.

Current path:

`producer → gateway → ingest → consumer group → warehouse`

## Containers and responsibilities

| Container | Responsibility | Operational truth |
|---|---|---|
| Gateway | Identity, envelope validation, queue acceptance | Returns `202` after queue write |
| Queue | Shared 24-hour buffer | One queue, no failover |
| Consumer group | Validate and land | Three normal replicas |
| Warehouse | Downstream record | Schema outside Platform |

## Primary runtime path

1. Producer sends stable event ID and request ID.
2. Gateway authenticates, validates, and writes to `ingest`.
3. Gateway returns `202` after queue acceptance.
4. Consumer validates and writes the warehouse.
5. Lookup and freshness expose later state.

## Failure and recovery boundaries

Consumer slowdown raises lag and depth. Queue saturation stops the shared
buffer. Gateway overload then affects every producer.

Adding one consumer replica is the safe local recovery control. Because every
producer shares the queue, current recovery is shared too.

## Trust and data boundaries

- Gateway terminates producer identity and enforces audience.
- Event bodies remain opaque to routing.
- Queue and warehouse credentials are runtime secrets.
- The proposed dispatcher adds no body store.

## Architecture facts and known gaps

- Cluster: `prod-ingest`; namespace: `ingest`; queue: `ingest`.
- Consumers: three normal, six maximum without approval.
- Retention: 24 hours.
- Gaps: no independent failure path, bounded shed response, or chaos proof.
