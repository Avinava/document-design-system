API contract

  # POST /events — companion to the spec

  

    **Source of truth:** `openapi/events.yaml` ·
    **Base path:** as declared in that file, not a hostname ·
    **Audience:** producer teams
  

  
## Auth

  
Service-to-service mTLS at the gateway, plus an audience claim on the caller identity. No API keys in query strings. This document does not include credentials.

  
## Resource map

  

    
Operations producers call

    

Method

Path

Success

Notes

    

      

`POST`

`/events`

202

Accepted for ingest. Body is the event.

      

`GET`

`/events/{id}`

200 / 404

Lookup by event ID. Not a list.

    

  

  
## Conventions

  

    - Idempotency. Repeat POST with the same id MUST NOT create a second warehouse row. Header Idempotency-Key MAY duplicate id.
    - Correlation. Echo X-Request-Id on every response.
    - Versioning. Breaking changes go to /v2. This companion is v1.
    - Errors. JSON object { "code", "message", "retryable" }.
  

  
## Worked examples

  
Success (synthetic):

  
```http
POST /events
{"id":"evt_01","type":"checkout.paid"}

202
{"id":"evt_01","status":"accepted"}
```

  
Error — queue shed (after RFC 014; today this is a 503):

  
```http
202
{"id":"evt_01","status":"shed","code":"INGEST_SHED","retryable":true}
```

  
## Error catalog

  

    
Stable codes

    

Code

Meaning

Client should

    

      

`INGEST_SHED`

Chosen queue unavailable

Retry with backoff

      

`INVALID_EVENT`

Body failed schema

Fix the payload; do not retry

    

  

  
## Spec ↔ implementation

  
OpenAPI still documents 503 on overload. Implementation after RFC 014 will return 202 + `INGEST_SHED`. Until the spec PR lands, treat the YAML as source and this paragraph as the known drift.

  
## Changelog

  
2026-08-12 — documented shed. No breaking change yet.
