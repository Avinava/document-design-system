Reference

  # Gateway environment

  
Keys the gateway reads. Values are never documented here. Structure matches the binary's flag set.

  

    
Gateway configuration keys

    

      

        
Key

        
Required

        
Meaning

      

    

    

      

`INGEST_QUEUE_URI`

yes

Queue endpoint. Current single queue, or dispatcher later.

      

`INGEST_GATEWAY_ADDR`

no

Bind address. Default `127.0.0.1:8443`.

      

`INGEST_SHED_MS`

no

Max wait before shed. Default 200. Unused until RFC 014.

    

  

  
## Process exit codes

  

    - 0 — clean shutdown.
    - 2 — configuration missing (usually INGEST_QUEUE_URI).
    - 3 — failed to bind INGEST_GATEWAY_ADDR.
  

  
No getting-started. No opinion about RFC 014. Those live elsewhere.
