Test report

  # Ingestion — RC 2026.08.12

  

    **Build:** `sha-a1b2c3d` ·
    **Environment:** staging ·
    **Date:** 2026-08-12 ·
    **Author:** Platform
  

  

    
**Verdict: go-with-waivers.** Functional and regression passed. Chaos test of a downed queue is waived until RFC 014 ships — that path does not exist on this build.

  

  
## Objective and scope

  
Regression on `POST /events` and consumer drain for release candidate 2026.08.12. Out of scope: dispatcher split (not merged), warehouse compaction, batch path.

  
## Results

  

    
Counts for this build only

    

Planned

Executed

Passed

Failed

Blocked

Skipped

    

      

40

38

36

0

0

2

    

  

  
38 of 40 executed (95%). 36 of 38 passed (95% of executed). Two skipped: chaos-down-queue, dual-write shadow — both RFC 014.

  
Verified: CI job ingest-test on sha-a1b2c3d.

  
## Defects

  
None open from this cycle. Waiver: no chaos coverage for single-queue fill (known; tracked by RFC 014).

  
## Environment

  
Staging. Runtime matching production minor. Browser matrix not applicable (service API). No private URLs, no credentials.

  
## Exit criteria

  

    - No P1/P2 open from the cycle — met.
    - Regression suite green — met.
    - Chaos on queue failure — waived, RFC 014.
  

  
## Residual risk

  
The failure mode in the 2026-07-30 postmortem is untested on this build because the second queue is not there. Shipping this RC does not reduce halt risk. That is a product risk, not a test escape.
