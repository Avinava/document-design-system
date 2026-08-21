ADR 009

  # Hash partitions on event ID, not producer ID

  

    **Status:** Proposed ·
    **Supersedes:** none ·
    **Owner:** Platform
  

  
## Context

  

    RFC 014 splits ingestion into `ingest-a` and `ingest-b`
    by partition. The partition key decides whether traffic is even under
    failure. Producers (Checkout, Catalog, Inventory) have very different
    volumes — Checkout alone is most of the 1.84M-unit ingestion footprint.
  

  

    Two forces are in tension: affinity (keep a producer's events on one queue
    so ordering is cheap) versus balance (keep both queues useful if one fails).
  

  
## Decision

  

    We will hash the partition on **event ID**, not producer ID.
    Ordering inside a producer is not a platform guarantee today and will not
    become one.
  

  
## Consequences

  

    - Load splits even when one producer dominates.
    - A producer cannot assume in-order delivery across the two queues. Callers that need order must impose it themselves.
    - Replaying a single producer's events means reading both queues. Operational runbooks have to say so.
