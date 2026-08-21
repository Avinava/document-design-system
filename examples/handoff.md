Handoff

  # Northwind Ingestion — engineering handoff

  

    **As of:** 2026-08-12 ·
    **Outgoing:** Platform ·
    **Incoming:** the incoming owner
  

  
## Scope and date

  

    Ownership of the ingestion path: gateway, the current single queue, consumers,
    and RFC 014 (proposed split). Warehouse ownership stays with Analytics.
  

  
## What it is

  

    Events enter at `POST /events`, buffer on `ingest`,
    land in the warehouse. Ingestion is 41% of platform footprint. See
    architecture and RFC 014.
  

  
## Current status

  

    - RFC 014 is Proposed, decision by 2026-09-01. Not shipped.
    - Open: consumer rebalance question; shed-versus-block (Reliability).
    - No unreleased branch except the RFC draft. Known bug: lag alert fires at 120s — too late (see postmortem 2026-07-30).
  

  
## How to run it

  
```bash
make ingest-test
make ingest-run   # needs ${INGEST_QUEUE_URI}
```

  
Verified: these targets exist in the Northwind Makefile used for this fiction.

  
## Where truth lives

  

    - Code: cmd/gateway, cmd/consumer.
    - Queue URI: property INGEST_QUEUE_URI — location, not value.
    - Dashboards: Ingestion / lag. Secrets: platform vault path ingest/*, never in git.
  

  
## Decisions that bind

  
Producer API is frozen (RFC 014 goal). Partition key is still Proposed (ADR 009). Verbal "we will not promise order" is now in that ADR — write it down before you leave.

  
## Risks and tripwires

  
A single queue fill still stops the platform. Do not restart the gateway to "clear" lag. Page at lag, then scale consumers, then escalate — runbook.

  
## Access

  
Request: ingestion namespace, lag dashboard, vault `ingest/*`. No credentials in this file.

  
## First-week checklist

  

    - Run make ingest-test.
    - Read RFC 014 and the 2026-07-30 postmortem.
    - Sit on one lag page with Platform still reachable.
  

  
## Open questions

  
Same two as RFC 014. Owner remains Reliability / Platform, 2026-08-25.
