Tutorial

  # Land your first event

  

    You will send one synthetic event through a local gateway and see it accepted.
    This is a lesson, not a production how-to. If you already run ingestion,
    use the how-to instead.
  

  
## You will

  

    - Start the local gateway.
    - POST one event.
    - Read the 202 and the event id.
  

  
## Start the gateway

  
```bash
make ingest-run
```

  
Wait until the log line contains `listening`. That is success for this step. Leave the process running.

  
## Post an event

  
In a second terminal:

  
```bash
curl -k -s -o /tmp/evt.json -w "%{http_code}" \
  https://127.0.0.1:8443/events \
  -d '{"id":"evt_learn","type":"tutorial.ping"}'
```

  
You should see `202`. Open `/tmp/evt.json` — it contains `evt_learn`.

  
## You are done

  

    You can accept an event locally. What the queue does under failure, how
    partitions work, and how to operate lag are other documents. Stop here.
