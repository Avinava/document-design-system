# Events API: accept once, identify clearly, retry safely

**Type:** API companion · v1
**Audience:** producer teams
**Authentication:** mTLS plus audience claim
**Source of truth:** `openapi/events.yaml`

This companion explains caller behavior. The OpenAPI file wins whenever the
two disagree.

## Operations

### `POST /events`

Validate and accept one event. Returns `202` with event ID and status.

### `GET /events/{id}`

Look up one event by opaque ID. Returns `200` or `404`; this is not a list.

## Caller conventions

- **Identity:** send a stable opaque `id`. Reusing an accepted ID must not
  create a second warehouse row.
- **Trace:** send `X-Request-Id`; the service echoes it.
- **Retry:** retry only when `retryable` is true, with bounded backoff.
- **Version:** breaking changes move to `/v2`.

## Request and response specimens

```http
POST /events
X-Request-Id: req_7f3
Content-Type: application/json

{"id":"evt_01","type":"checkout.paid"}

202 Accepted
{"id":"evt_01","status":"accepted"}
```

Acceptance means the event reached the current queue, not the warehouse.

Proposed RFC 014 shed behavior:

```http
202 Accepted
X-Request-Id: req_7f4

{"id":"evt_02","status":"shed",
 "code":"INGEST_SHED","retryable":true}
```

## Error catalog

| Code | Meaning | Retry? | Caller action |
|---|---|---|---|
| `INGEST_SHED` | Selected queue unavailable | Yes | Resend same ID with backoff |
| `INVALID_EVENT` | Envelope failed schema | No | Correct payload |
| `UNAUTHORIZED_PRODUCER` | Identity or audience rejected | No | Correct service identity |

## Known specification drift

OpenAPI and the current implementation still return `503` on queue overload.
The `202 + INGEST_SHED` response is proposed and must not be treated as current
until the source changes.

Last companion review: 2026-08-18.
