Architecture

  # Northwind Ingestion — current state

  

    **As of:** 2026-08-12 ·
    **This is current, not proposed.** RFC 014 is the change. ·
    **Owner:** Platform
  

  
## Boundary

  
This application owns accept, buffer, and land of first-party and partner events. It does not own checkout, catalog, or the warehouse schema.

  
## System context

  
Checkout, Catalog, and Inventory call `POST /events`. The warehouse is downstream. On-call watches lag. Verified: gateway listeners and consumer writes.

  
## Containers

  

    - Gateway — HTTP, auth, schema check.
    - Queue ingest — one queue, no failover. 41% of platform footprint sits behind it.
    - Consumer — writes the warehouse.
  

  
The dispatcher and `ingest-a/b` are Proposed, not current. They do not appear on this map.

  
## Primary runtime path

  
Producer → gateway → enqueue on `ingest` → consumer → warehouse. On queue full, the gateway blocks and then 503s. There is no shed path yet.

  
## Data

  
Event body is JSON as declared in `openapi/events.yaml`. Transforms: none in this service; the warehouse maps fields.

  
## Failures

  
Consumer crash: lag climbs, runbook scales replicas. Queue unavailable: producers fail. No retry-with-shed. Verified: 2026-07-30 postmortem.

  
## Trust boundaries

  
mTLS at the gateway. Queue URI from `${INGEST_QUEUE_URI}`. This document does not name hosts or secrets.

  
## Extension points

  
A new event type is a schema addition at the gateway plus a warehouse mapping. A new producer is an identity grant, not a new queue — until RFC 014.

  
## Known gaps

  
Whether two queues fail independently is Unresolved. Partner-feed volume is not in the 41% snapshot — excluded population, same as the analytical report.
