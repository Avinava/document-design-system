# Northwind partner ingest: start with the map, then open the owning document

**Type:** Mule application documentation suite
**Kind:** adaptive suite
**Application:** partner-ingest
**Owner:** Platform
**Reviewed:** 2026-08-18

The application accepts partner events over HTTP, validates RAML, transforms
them into the Northwind envelope, and posts to `/events`. It does not own
warehouse schema, producer identity policy, or queue topology.

## Two-minute orientation

Partner-specific shape ends at the transformation. Retry and identity after
that point follow the Northwind Events API.

## Documents in this set

| Document | Reader question | Emit when |
|---|---|---|
| `README.md` | What is this and where do I start? | Always |
| `docs/architecture.md` | How do listeners, flows, and dependencies connect? | Always |
| `docs/api-contract.md` | What does RAML require and how is it mapped? | Always |
| `docs/onboarding.md` | How do I run one partner fixture? | Always |
| `docs/runbook.md` | How do I operate app-specific controls? | Evidence exists |
| `docs/test-report.md` | Can this named build ship? | Named release decision |

## Ownership and flow inventory

| Flow | Trigger | Responsibility | Failure owner |
|---|---|---|---|
| `partner-http` | Partner POST | Auth, RAML, request ID | partner-ingest |
| `to-northwind-event` | Valid message | Map to event envelope | partner-ingest |
| `publish-event` | Mapped event | Call `POST /events` | Shared with Events API |
| `retry-or-dead-letter` | Retryable failure | Bound retries, preserve ID | partner-ingest |

## Evidence and freshness rules

1. RAML and Mule configuration own listeners, routes, and transformations.
2. MUnit supports named test claims; absent tests are not inferred passes.
3. Deployment files own environments and required configuration.
4. Northwind OpenAPI owns downstream event behavior.
5. Record conflicts in the owning document rather than smoothing them over.

Generate only documents supported by evidence. Four complete pages are better
than a catalog of empty headings.
