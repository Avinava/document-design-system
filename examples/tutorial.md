# Follow one event from local request to accepted identity

**Type:** Tutorial · first successful path
**Time:** 20 minutes
**Prerequisites:** Go 1.22, Make, Docker
**Production access:** none

You will start the local gateway, send one synthetic event, inspect its
response, and prove that replaying the same identity does not create a second
logical event.

## Start from a known-good build

```bash
make ingest-test
```

Checkpoint: contract and consumer suites pass. Stop if the baseline is broken.

## Start the local gateway

```bash
make ingest-run
```

Leave the process running when the log reports `listening` on port 8443.

## Send one synthetic event

```bash
curl -k -i https://127.0.0.1:8443/events \
  -H 'X-Request-Id: req_tutorial_01' \
  -d '{"id":"evt_learn","type":"tutorial.ping"}'
```

Checkpoint: response is `202`, echoes the request ID, and returns
`{"id":"evt_learn","status":"accepted"}`.

## Repeat the identity and inspect the result

Run the same request without changing `evt_learn`. The service may return the
original acceptance or an idempotent acknowledgement, but it must not create a
second warehouse row.

## Stop at the lesson boundary

You can start the service, send an event, read acceptance correctly, and explain
why replay keeps the same ID. Failure recovery and production operation belong
to the how-to and runbook.
