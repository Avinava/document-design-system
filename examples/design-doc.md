Design document

  # RFC 014 — Splitting the ingestion path

  

    **Status:** Proposed ·
    **Decision needed by:** 2026-09-01 ·
    **Owner:** Platform
  

  

    
Change log

    

Date

Change

By

    

      

2026-08-12

Added rollback plan after review

Platform

      

2026-08-08

Initial draft

Platform

    

  

  

    
Contents

    

      - Problem
      - Goals and non-goals
      - Design
      - Alternatives considered
      - Cross-cutting
      - Risks
      - Rollout
      - Open questions
    

  

  
## Summary

  

    The ingestion path holds 41% of the platform footprint behind a single queue
    with no failover. This proposes splitting it into two independently
    deployable paths so that a queue failure degrades throughput rather than
    stopping ingestion.
  

  
## Problem

  

    Four of the last six incidents traced to the same coupling.1
    Each began as queue backpressure and ended as a full ingestion stop, because
    every producer shares one path. Ingestion is 41% of included footprint
    (1.84M of 2.50M units) — a halt is not a corner case.
  

  
Verified: incident tickets 2026-03-14, 2026-04-02, 2026-06-19, 2026-07-30. Inventory snapshot as of 2026-08-12.

  
## Goals and non-goals

  

    - A queue failure degrades throughput instead of halting ingestion.
    - Recovery without a coordinated redeploy of every producer.
    - No change to the producer-facing API at /events.
  

  

    

      This does **not** propose replacing the queue technology,
      changing the retention policy, or touching the batch path. Those are real
      questions and they are not this document's questions.
    

  

  
## Design

  

    Route producers through a thin dispatcher that writes to one of two queues
    keyed by partition. Each queue has its own consumer group and its own
    failover. The dispatcher is stateless and deployable independently.
  

  
```yaml
dispatcher:
  routes:
    - match: {partition: even}
      queue: ingest-a
    - match: {partition: odd}
      queue: ingest-b
  on_queue_unavailable: shed_and_alert
```

  
## Alternatives considered

  

    - Do nothing. Cost: the incident pattern continues at
      roughly one per quarter.
    - Larger single queue. Raises the backpressure threshold
      without removing the single point of failure. Rejected because it changes
      when the incident happens, not whether.
    - Per-producer queues. Removes the coupling entirely, but
      multiplies operational surface by the producer count. Rejected on cost.
  

  
## Cross-cutting

  

    - Observability. Per-queue lag and dispatcher shed counts become first-class dashboards before rollout.
    - Security. The producer-facing auth at the gateway does not change. The dispatcher inherits the gateway's identity.
    - Privacy. Payloads are unchanged; this is a routing change, not a new store.
  

  
## Risks and mitigations

  

    - Partition skew sends most traffic to one queue. Mitigated by hashing on event ID rather than producer ID.
    - Dispatcher becomes the new single point of failure. Mitigated by running it stateless behind the existing load balancer.
  

  
## Rollout

  

    Dual-write to `ingest` and the new pair for one week, shadow-consume
    `ingest-a/b`, then cut reads. Rollback is a DNS/flag flip back to
    the single queue; the old path stays until the shadow week ends.
  

  
## Open questions

  

    - Does the consumer group rebalance cleanly under partial failure? — Owner: Platform, by 2026-08-25
    - Is shed-and-alert the right behavior, or should the dispatcher block? — Owner: Reliability, by 2026-08-25
  

  

    
## Notes

    

      Incidents 2026-03-14, 2026-04-02, 2026-06-19, 2026-07-30. ↩
