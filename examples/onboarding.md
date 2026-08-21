Onboarding

  # Run Northwind Ingestion locally

  

    **Owner:** Platform ·
    **Dated:** 2026-08-12 ·
    **For:** first day, not an incident
  

  
## Prerequisites

  

    - Go 1.22, Make, Docker. Verified: CI setup-go 1.22.
    - Access request: ingestion namespace (staging), vault path ingest/*. Values never in this file.
  

  
## Safe configuration

  
```env
INGEST_QUEUE_URI=${INGEST_QUEUE_URI}
INGEST_GATEWAY_ADDR=127.0.0.1:8443
```

  
Copy `.env.example`. Do not paste production URIs.

  
## Local commands

  
```bash
make ingest-test
make ingest-run
```

  
Success: tests pass; gateway logs "listening" on 8443.

  
## External systems

  
Local Docker Compose provides a stand-in queue. Staging queue is not required on day one.

  
## Deployment

  
Staging deploys from `main` via the ingest workflow. You will not deploy on day one.

  
## Validation

  

    - curl -k https://127.0.0.1:8443/events with the example body in docs/api.md → 202.
    - Consumer log shows the event id.
  

  
## Troubleshooting

  
`connection refused` on 8443: `make ingest-run` is not up. `INGEST_QUEUE_URI unset`: the example env file was not copied.
