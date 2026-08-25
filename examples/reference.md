# Gateway configuration and process behavior

**Type:** Runtime reference · gateway v1
**Reviewed:** 2026-08-18
**Source:** deployment manifest and CI

Lookup facts only: required keys, defaults, health paths, exit codes, and
validation commands.

## Configuration keys

| Key | Required | Default | Meaning |
|---|---|---|---|
| `INGEST_QUEUE_URI` | Yes | — | Queue endpoint; dispatcher URI after RFC 014 |
| `INGEST_GATEWAY_ADDR` | No | `127.0.0.1:8443` | Bind address |
| `INGEST_SHED_MS` | No | `200` | Proposed dispatcher wait |
| `INGEST_LOG_LEVEL` | No | `info` | `debug`, `info`, `warn`, or `error` |

## Process endpoints

- `GET /health/live` — process is running; does not prove queue access.
- `GET /health/ready` — required configuration exists and queue is reachable.
- `GET /metrics` — request, enqueue, shed, and error metrics.

## Process exit codes

| Code | Meaning | Operator response |
|---:|---|---|
| `0` | Clean shutdown | None |
| `2` | Required configuration missing | Check `INGEST_QUEUE_URI` |
| `3` | Bind failed | Check address and port ownership |
| `4` | Queue unavailable at startup | Check dependency and readiness policy |

## Validation commands

```bash
make ingest-test
make ingest-run
curl -k https://127.0.0.1:8443/health/ready
```

Expected readiness response: `200` with `{"status":"ready"}`. Procedures and
rationale live in their owning documents.
