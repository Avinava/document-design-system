# World — Northwind Ingestion

Shared fiction for every example in this repo — writing-documents, the capacity deck, the inventory report, and the figures. Writers treat these as facts. Do not invent a second company.

## Product

**Northwind Ingestion** takes events from first-party apps and partner feeds, buffers them, and lands them in a warehouse the rest of the platform reads.

It is an internal platform capability, not a customer-facing product. Operators are the Platform team. Callers are producer services (Checkout, Catalog, Inventory).

## Components (Verified in this repo's examples)

| Name | Role |
|---|---|
| Gateway | Producer-facing HTTP API. Path `/events`. Unchanged by RFC 014. |
| Dispatcher | Proposed. Stateless. Routes by partition. |
| Queue `ingest` | Current single queue. No failover. **41% of platform footprint** sits behind it. |
| Queues `ingest-a` / `ingest-b` | Proposed split, even/odd partition. |
| Consumer groups | Read a queue into the warehouse. |
| Warehouse | Downstream. Out of scope for the split. |
| Batch path | Separate. Explicit non-goal of RFC 014. |

## Numbers (keep consistent)

- Footprint concentration: **41%** of included units on ingestion (1.84M of 2.50M). Same figure as the analytical report and the capacity deck.
- Incidents tracing to the coupling: **4 of the last 6** (2026-03-14, 2026-04-02, 2026-06-19, 2026-07-30).
- Cadence: roughly **one such incident per quarter** if nothing changes.
- Decision needed by: **2026-09-01**. RFC opened 2026-08-08.

## Status in this universe

| Claim | State |
|---|---|
| Single queue, no failover | Verified |
| 41% footprint on ingestion | Verified (inventory snapshot, same as the report) |
| Four of six incidents from this coupling | Verified (incident tickets) |
| Split into two paths | Proposed (RFC 014, not shipped) |
| Shed-and-alert vs block | Unresolved (Reliability, 2026-08-25) |
| Consumer rebalance under partial failure | Unresolved (Platform, 2026-08-25) |
| Business-criticality "ingestion must not fully stop" | Provided (Platform lead) |

## People (roles, not real identities)

- **Platform** — owns ingestion. Author of RFC 014.
- **Reliability** — reviews failure behaviour.
- **Checkout / Catalog / Inventory** — producer teams; callers of `/events`.
- Incoming engineer in the handoff: "the incoming owner". Outgoing: "Platform".

## Brand

Documents sent outside the team wear **Horizon** (`data-theme="horizon"`). The guide is the worked example in `skills/brand-theme-design/references/mapping.md`: primary `#0B5FFF`, ink `#101828`, slate `#475467`, cloud `#F2F4F7`. Söhne is licensed and is not redistributed; Inter is the metric fallback.

Ops and internal notes stay on `field-notes` or `console-violet`. Board packets that are not wearing the client brand stay on `executive-navy`.

## What is in-repo here

This document-design-system repository is *not* Northwind. The examples pretend to be Northwind documents living in a Northwind repo (`docs/adr/`, `docs/runbooks/`, …). Commands, property keys, and paths are synthetic. No secrets, no real hostnames — `api.example.invalid`, `${INGEST_QUEUE_URI}`.
