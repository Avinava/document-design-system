# Partition on event ID, not producer ID

**Type:** Architecture decision record · ADR 009
**Status:** Accepted
**Date:** 2026-08-18
**Owner:** Platform
**Supersedes:** none

## Decision

The dispatcher will compute `hash(event.id) mod 2`. Even partitions go to
`ingest-a`; odd partitions go to `ingest-b`.

## Context

Checkout contributes most of the 1.84M-unit ingestion footprint. Partitioning
by producer would preserve producer-local ordering, but it would also place
most traffic and failure exposure on one queue.

The platform does not promise ordered delivery across events from one producer.
Creating that promise inside this change would expand the API contract.

## Alternatives rejected

- **Producer ID:** cheap affinity, but known traffic skew makes one queue
  dominant and weakens isolation.
- **Round robin:** balances writes but is not deterministic, complicating
  retries, replay, and diagnosis.

## Consequences

Benefits:

- Dominant producers distribute across both queues.
- Retries route to the same partition.
- One queue failure leaves a useful healthy path.

Costs:

- Producer replays must read both queues.
- Callers cannot infer ordering from queue placement.
- Runbooks and dashboards must name the partition.

This record becomes immutable when RFC 014 ships. A future ordering guarantee
requires a new ADR.
