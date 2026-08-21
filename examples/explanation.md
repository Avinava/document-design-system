Explanation

  # Why ingestion fails as a whole

  

    Backpressure is ordinary. A full stop of every producer is not a necessary
    consequence of it. This page is why Northwind currently treats them as the
    same event — and why RFC 014 is a routing change, not a capacity change.
  

  
## One path, many callers

  

    Checkout, Catalog, and Inventory all share `/events` and one
    queue. That sharing is the feature: producers do not run their own brokers.
    It is also the failure domain. When the queue cannot accept, the gateway
    has nowhere to put work, so it stops accepting. 41% of platform footprint
    is downstream of that decision.
  

  
## It is not (only) size

  

    A larger queue delays the halt. It does not create a second place for work
    to go. Detection at 120s of lag delays the page. It does not create a
    degrade path. Those are real improvements; they answer a different why.
  

  
## Degrade means a defined leftover

  

    "Degrade throughput" only means something if a producer can still land
    *some* events. Two queues, or a shed that returns 202, are ways to
    leave a leftover. Blocking until 503 leaves none.
  

  

    How to split, how to replay, how to page: other documents. This one is the
    picture that makes those procedures make sense.
