How-to

  # How to replay a shed event

  
For someone who already runs ingestion. Goal: take an event that was shed and land it without duplicating a warehouse row.

  
## Before you start

  

    - You have the event id and the shed timestamp from the dispatcher log.
    - RFC 014 is in shadow or later. On today's single queue this how-to does not apply — there is no shed path.
  

  
## Steps

  

    - Confirm the warehouse has no row for that id. If it does, stop. Idempotency already did the job.
    - POST /events with the same body and the same id. Do not mint a new id.
    - Expect 202. If you get INVALID_EVENT, fix the payload; do not retry blindly.
    - If you get INGEST_SHED again, the chosen queue is still down — wait, do not hammer.
  

  
## You are done when

  
Warehouse has one row for that id, and the shed dashboard does not increment on the replay.
