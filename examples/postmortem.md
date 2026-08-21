Postmortem

  # Ingestion halt — 2026-07-30

  

    **Status:** Draft ·
    **When:** 2026-07-30 14:12–16:04 UTC ·
    **Owner:** Platform
  

  
## Summary

  

    The single ingestion queue filled. Every producer sharing that path stopped
    accepting events for 1 hour 52 minutes. Warehouse freshness lagged. This is
    the fourth incident of this shape in six events.
  

  
## Impact

  

    - Duration: 1h 52m (detect 14:12 UTC, recover 16:04 UTC).
    - Checkout, Catalog, and Inventory producers returned 503 or blocked.
    - Warehouse lag peaked at 118 minutes of events.
  

  
Verified: pager timestamps; gateway 5xx from the 14:12–16:04 window.

  
## Timeline (UTC)

  

    - 14:12 — lag alert. Detection.
    - 14:18 — on-call confirms queue depth saturating; consumers alive.
    - 15:40 — producers start failing hard as the gateway times out.
    - 16:04 — queue drained after a consumer scale-up; ingestion resumes.
  

  
## Root cause

  

    One queue, no failover. Backpressure had nowhere to go except the gateway.
    Scaling consumers recovered this instance; it does not remove the coupling.
    RFC 014 exists because of this chain.
  

  
## Contributing factors

  

    - Detection waited on lag &gt; 120s — five minutes of fill before a page.
    - No shed-and-alert path; the gateway blocked.
  

  
## What went well

  
On-call found the lag dashboard on the first try. The runbook scale step worked.

  
## Action items

  

    - Ship RFC 014 (two queues). Owner: Platform. P1. Tracking: RFC 014.
    - Page at 60s lag, not 120s. Owner: Reliability. P2.
