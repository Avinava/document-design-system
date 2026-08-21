Specification

  # Dispatcher routing — Northwind Ingestion

  

    **Status:** Proposed ·
    **Keywords:** RFC 2119 ·
    **Owner:** Platform
  

  

    The key words MUST, SHOULD, and MAY in this document are to be interpreted
    as described in RFC 2119.
  

  
## Scope

  

    This specifies the dispatcher introduced by RFC 014: how an accepted
    `POST /events` payload is assigned to `ingest-a` or
    `ingest-b`. It does not specify the gateway API, warehouse
    schema, or batch path.
  

  
## Definitions

  

    - Event ID — the id field on an accepted event. Opaque string.
    - Partition — hash(event id) mod 2. Even → ingest-a. Odd → ingest-b.
  

  
## Requirements

  

    - REQ-001 The dispatcher MUST assign every accepted event to exactly one of ingest-a or ingest-b.
    - REQ-002 The assignment MUST be a function of event ID alone.
    - REQ-003 If the chosen queue is unavailable, the dispatcher MUST shed the event and emit an alert. It MUST NOT block the gateway request for more than 200ms. (Unresolved vs blocking: Reliability, 2026-08-25.)
    - REQ-004 The dispatcher MUST NOT inspect or persist payload bodies.
  

  
## Examples

  

    Event `id=evt_01` hashes even → `ingest-a`. Event
    `id=evt_02` hashes odd → `ingest-b`. A 503 from
    `ingest-a` yields HTTP 202 from the gateway, a shed count, and
    no warehouse write.
  

  
## Compliance

  

    Conformance is a unit test of `REQ-001`–`REQ-002` on a
    fixed ID list, plus a chaos test that `ingest-a` down does not
    stall `/events` past 200ms.
