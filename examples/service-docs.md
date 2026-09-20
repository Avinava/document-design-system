# Northwind Ingestion documentation starts with ownership, not page count

**Kind:** Adaptive service suite<br>
**Owner:** Platform<br>
**Reviewed:** 2026-11-20

## Two-minute orientation

Northwind Ingestion accepts events, buffers them, and lands them in the
warehouse. Platform owns the runtime. Producer teams own payload quality and
retry behavior. Warehouse schema remains outside the service.

## Document map

| Owner | Document | Reader question |
|---|---|---|
| Service index | `README.md` | What is this and where do I start? |
| Current system | `docs/architecture.md` | How is it arranged today? |
| Interface | `docs/api.md` | How do I call it correctly? |
| Operations | `docs/runbooks/` | What do I do right now? |
| Support | `docs/support-model.md` | Who responds and when? |
| Learning | `docs/onboarding.md` | How do I prove it works? |

## Freshness

Architecture and support review on every production change. Runbooks review
after use. API documentation follows the machine definition. Test reports and
release notes belong to named versions such as v2.0.0, not permanent stubs.
