# Take ownership without rediscovering the failure boundaries

**Type:** Engineering handoff · Northwind Ingestion
**As of:** 2026-08-18
**From:** Platform
**To:** incoming owner
**Scope:** gateway through warehouse landing

## Current status in one minute

- Production still uses one queue, `ingest`, with no failover.
- RFC 014 is proposed; ADR 009 is accepted for the partition key.
- The 2026-07-30 incident recovered through consumer scaling.
- Release candidate `sha-8132c3` is go-with-waivers.

## Prove the local service before changing it

1. Run `make ingest-test`; contract and consumer tests must pass.
2. Run `make ingest-run`; logs must contain `listening` on 8443.
3. Send one synthetic event:

   ```bash
   curl -k https://127.0.0.1:8443/events \
     -d '{"id":"evt_handoff","type":"handoff.ping"}'
   ```

   Success is `202` with `evt_handoff` repeated in the response.

## Where truth lives

| Concern | Source |
|---|---|
| Producer behavior | `openapi/events.yaml` |
| Runtime configuration | deployment manifests |
| Operations | *Ingestion / lag* dashboard and runbook |
| Proposed change | RFC 014 and ADR 009 |

## Tripwires and in-flight work

- Do not claim the split path or `INGEST_SHED` response is live.
- Never change event-ID idempotency without API review.
- Never delete a queue as rollback or mitigation.
- Reliability owns shed-versus-block approval.
- The catalog backfill is the opportunity cost if RFC 014 is funded.

## First-week checklist

- Run the local proof.
- Shadow one Platform on-call review.
- Read RFC 014, ADR 009, the API companion, and latest postmortem.
- Reconcile dashboard queue names with deployment configuration.
- Record access gaps outside this document; never add credentials.

Handoff is complete when the incoming owner can explain current, proposed, and
unresolved state and name the safe incident control.
