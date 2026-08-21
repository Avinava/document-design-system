Runbook

  # Ingestion queue lag is climbing

  

    **Owner:** Platform ·
    **Dated:** 2026-08-12 ·
    **Trigger:** `ingest_lag_seconds` &gt; 120 for 5 minutes
  

  
## When to use

  
Page: `ingest_lag_seconds` above 120s for five minutes, or a producer report that `POST /events` is 202-shedding.

  
## Preconditions

  

    - On-call has kubectl access to the ingestion namespace.
    - Dashboard: Ingestion / lag (no credentials in this document).
  

  
## Steps

  

    - Open the lag dashboard. Confirm which queue (ingest today; ingest-a or ingest-b after RFC 014). Success: one queue named.
    - Check consumer restart count. If crashing, jump to Escalation.
    - If consumers are up and lag is still climbing, scale the consumer group by one replica:
      
```bash
kubectl -n ingest scale deploy/ingest-consumer --replicas=$(($(kubectl -n ingest get deploy/ingest-consumer -o jsonpath='{.spec.replicas}')+1))
```

      Success: replica count increased by one; lag slope flattens within three minutes.
    - If lag does not flatten, shed is already happening at the dispatcher — do not restart the gateway. Go to Escalation.
  

  
## Verification

  
`ingest_lag_seconds` falling for ten minutes, and `POST /events` p99 under 200ms.

  
## Rollback

  
Scale the consumer group back to the previous replica count. Do not delete queues.

  
## Escalation

  
After 15 minutes without a falling lag, or any consumer crashloop: page Platform primary, then Reliability. Stop changing replica counts.
