# Platform owns ingestion support with Reliability as the failure escalation

**Effective:** 2026-11-02<br>
**Service owner:** Platform<br>
**Review:** 2026-11-20

## Coverage and intake

Platform owns business-hours support and the existing on-call path for P1/P2
incidents. Operator questions enter through the service channel; alerts page
the on-call path.

## Priority and response contract

| Priority | Definition | First owner |
|---|---|---|
| P1 | Event acceptance stopped for multiple producers | Platform on-call |
| P2 | One queue impaired or lag rising without full stop | Platform on-call |
| P3 | Non-urgent defect or documentation gap | Platform backlog |

## Escalation and boundaries

After 15 minutes without falling lag, or on any crash loop, Platform escalates
to Reliability and stops replica changes. Producer payload quality belongs to
Checkout, Catalog, and Inventory. Warehouse schema remains outside the service.

Runbooks own execution; this document owns who responds and when.
