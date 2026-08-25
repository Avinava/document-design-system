# Replay a shed event without creating a duplicate

**Type:** How-to · producer recovery
**Audience:** producer engineers
**Time:** 10 minutes
**Applies after:** RFC 014 shed behavior ships

Use the original event ID, confirm it did not already land, and retry only when
the response marks the failure as retryable.

## Before you start

- You have event ID and request ID from the original response.
- The code is `INGEST_SHED` with `retryable: true`.
- You have not changed the payload.

Do not invent a new ID. A new ID bypasses idempotency and may create a second
warehouse row.

## Replay procedure

1. Check whether the event already landed:

   ```bash
   curl -s https://api.example.invalid/events/evt_02
   ```

   Continue only on `404`; `200` means the original attempt succeeded.

2. Wait for the bounded exponential-backoff window from producer policy.
3. Resend the unchanged event:

   ```bash
   curl -X POST https://api.example.invalid/events \
     -H 'X-Request-Id: req_replay_01' \
     -d '{"id":"evt_02","type":"checkout.paid"}'
   ```

4. Verify by ID. Stop after the producer policy’s maximum attempts and
   escalate rather than changing identity.

## You are done when

Lookup returns exactly one `evt_02`, the replay response is recorded with its
request ID, and the shed counter does not increase again for that attempt.
