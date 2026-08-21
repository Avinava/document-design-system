Proposal

  # Two engineers, one quarter, to split ingestion

  

    **Ask of:** Platform director ·
    **Needed by:** 2026-09-01 ·
    **Author:** Platform
  

  
## The ask

  

    Two engineers for one quarter to ship RFC 014 — split the ingestion queue
    so a single queue failure degrades throughput instead of stopping ingestion.
  

  
## Rationale

  

    Four of the last six incidents ended as a full ingestion stop. Ingestion is
    41% of platform footprint. Doing this later, during a worse incident, costs
    more than a planned quarter.
  

  
Verified: incident list and inventory snapshot in RFC 014.

  
## Cost

  

    - Two engineers, twelve weeks. Opportunity cost: the catalog backfill slips a quarter.
    - Ongoing: one extra queue and consumer group to operate.
    - Hard to quantify: pages we do not take when the next backpressure arrives.
  

  
## Alternatives

  

    - Do nothing. Continue at roughly one halt per quarter.
    - Larger single queue. Cheaper this quarter; does not remove the failure mode. Rejected in RFC 014.
  

  
## Decision needed

  

    Platform director, by 2026-09-01. If there is no decision, the default is
    do nothing — which is a choice, and should be recorded as one.
