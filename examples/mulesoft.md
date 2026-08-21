MuleSoft suite

  # Northwind partner ingest — documentation set

  

    **Kind:** suite, not one file ·
    **If mule-docs is installed:** prefer it for inventory ·
    **This page:** designed index of the Markdown set
  

  

    A fictional Mule 4 application that accepts partner events and hands them
    to Northwind Ingestion's `/events`. Claims below are labelled.
    No Anypoint topology is invented. No secrets.
  

  
## Documents in this set

  

    
Adaptive suite

    

File

Why it exists

    

      

`README.md`

Two-minute orientation

      

`docs/architecture.md`

HTTP listener → transform → Northwind `/events`

      

`docs/api-contract.md`

RAML present — partner-facing POST

      

`docs/onboarding.md`

POM and MUnit commands in CI

    

  

  
No operations doc: no scheduler, queue, or batch in the (fictional) source. No flow catalog: fewer than ten top-level flows.

  
## What this application owns

  

    Partner HTTP in, DataWeave mapping to the Northwind event shape, POST to
    the gateway. It does not own the warehouse or RFC 014.
    Inferred from a conventional Mule layout for this example — there is no real `src/main/mule` in *this* repo.
  

  
## Evidence rules used

  

    - Property keys only (${NWIN_EVENTS_URI}), never values.
    - Hostnames: api.example.invalid.
    - MUnit summarised by behaviour (happy path, HTTP 4xx mapping), not suite count.
  

  
Markdown twins for a real project would live next to that project's code. This HTML is the gallery rendering of the same suite.
