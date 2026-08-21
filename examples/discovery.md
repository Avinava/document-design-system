Discovery

  # Should we split ingestion, or is the problem somewhere else?

  

    **Decision this enables:** go to RFC 014 / stop / reframe ·
    **Window:** 2026-07-01 – 2026-08-08 ·
    **Owner:** Platform
  

  
## Goal of this discovery

  
Decide whether a queue split is the right next investment, or whether detection, consumer capacity, or producer behaviour would remove more halt time cheaper.

  
## Problem as reframed

  

    Not "we need two queues". The problem: when ingestion backpressures, the
    whole platform stops accepting events, and that has happened four times in
    six incidents.
  

  
## Users and context

  
Operators (Platform on-call). Producer teams who feel the 503s. Downstream analysts who wait on the warehouse. Wider journey: checkout write → event → warehouse → inventory views.

  
## Evidence

  

    - 6 incident tickets in 2026; 4 share the queue-fill chain. Verified.
    - 3 on-call interviews (Platform). All named lag-alert delay as well as the single queue. Verified method; n=3.
    - "Ingestion must not fully stop" as a business rule. Provided: Platform lead.
  

  
## Opportunities

  

    - Remove the single point of failure (queue split).
    - Detect earlier (60s lag, not 120s).
    - Degrade instead of block (shed-and-alert) even on one queue.
  

  
## Constraints

  

    - Hard: producer API at /events stays. Changing it is a multi-team contract.
    - Soft: consumer count and alert thresholds. Those we can change next week.
  

  
## Alternatives to building

  
Page earlier and scale consumers — cheaper, does not stop a full fill. Doing nothing remains the default if this discovery recommends stop.

  
## Assumptions still open

  

    - Two queues actually fail independently — untested. Highest build risk.
    - Shed-and-alert is acceptable to Checkout. Not yet asked.
  

  
## Recommendation

  
**Proceed** to RFC 014, and also lower the lag alert in parallel. Stopping would accept another halt this quarter; the cost of being wrong on the split is one extra queue to run, not a new user-facing surface.

  
## What would be tested next

  
Shadow-consume on a second queue for a week (RFC 014 rollout). Ask Checkout whether 202-shed is tolerable.
