# Recover when ingestion queue lag keeps climbing

**Type:** Operational runbook · RB-INGEST-01
**Owner:** Platform
**Reviewed:** 2026-08-18
**Trigger:** `ingest_lag_seconds > 120` for five minutes
**Escalate at:** 15 minutes

Use this procedure after the lag alert fires or producers report blocked or
failed event acceptance.

## Before changing anything

- Confirm access to the `ingest` namespace and *Ingestion / lag* dashboard.
- Start an incident note with page time, lag, depth, replicas, and request p99.
- Do not restart the gateway or delete a queue.

## Recovery procedure

1. **Name the failing boundary.** Identify the queue whose lag is rising.
   Record lag slope and affected producers.
2. **Check consumer health before scaling.** If any consumer crash-loops, go
   directly to escalation.

   ```bash
   kubectl -n ingest get deploy/ingest-consumer
   kubectl -n ingest get pods -l app=ingest-consumer
   ```

3. **Add one consumer replica.** Do not exceed six without Reliability.

   ```bash
   kubectl -n ingest scale deploy/ingest-consumer \
     --replicas=$((CURRENT_REPLICAS + 1))
   ```

4. **Observe for three minutes.** Watch lag, queue depth, p99, and errors.
   - If lag falls, verify recovery.
   - If lag is flat, observe two more minutes.
   - If lag rises or a consumer crashes, escalate.

## Verify, rollback, or escalate

- **Verify:** lag falls for ten minutes and `POST /events` p99 stays below
  200 ms.
- **Rollback:** remove the added replica if it causes errors. Never delete a
  queue.
- **Escalate:** after 15 minutes, any crash loop, or rising 5xx, page Platform
  primary and Reliability and stop local changes.

Record final replica count, recovery time, peak lag, and whether the documented
control changed the slope.
