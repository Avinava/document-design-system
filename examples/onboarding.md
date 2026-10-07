# Build the right model of Northwind Ingestion before you operate it

**Type:** Engineering onboarding
**Time:** 55 minutes
**Audience:** incoming platform engineer
**Environment:** local only
**Owner:** Platform

Read the current path, learn where familiar queue assumptions fail, run one
event locally, and finish with the questions worth asking on your first on-call
review.

**Learning goal.** By the end, you can:

- draw the current path and mark its single failure boundary;
- run one synthetic event locally and read its `202` correctly;
- separate current, proposed, and unresolved facts without production access.

## The working model

Northwind Ingestion is an internal acceptance and landing path. Producers send
events to the gateway; one shared queue buffers them; consumers validate and
write them to the warehouse.

Carry this sentence: the current queue is both the buffer and the failure
boundary for every first-party producer.

The proposed dispatcher and split queues in RFC 014 are not production facts.

## Four boundaries that prevent wrong assumptions

1. **Acceptance:** `202` means queued, not warehoused.
2. **Identity:** event ID is the retry anchor; reuse it.
3. **Ordering:** producer-local order is not guaranteed.
4. **Rollback:** traffic flips back; queues are never deleted.

## Read the request path without running it

```http
POST /events
X-Request-Id: req_7f3

{"id":"evt_01","type":"checkout.paid"}

202 {"id":"evt_01","status":"accepted"}
```

Follow event ID for idempotency, request ID for tracing, and status for caller
behavior. Then read configuration in this order: queue URI, bind address,
health endpoints, and alert thresholds.

## Run one event locally

1. Run `make ingest-test`; contract and consumer tests must pass.
2. Run `make ingest-run`; wait for `listening` on 8443.
3. Send the synthetic event:

   ```bash
   curl -k https://127.0.0.1:8443/events \
     -d '{"id":"evt_learn","type":"onboarding.ping"}'
   ```

   Success is `202` with `evt_learn` repeated.

## Prove readiness with understanding, not task completion

- Draw the current path and mark the single failure boundary.
- Explain why scaling consumers recovers but does not prevent recurrence.
- Name current and proposed overload responses without mixing them.
- Locate the runbook, API source, RFC, ADR, dashboard, and postmortem.
- Ask who approves shed behavior and where chaos testing will run.

You are ready when you can explain what is current, proposed, unresolved, and
safe to change without relying on production access.
