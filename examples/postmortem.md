# One full queue stopped every ingestion producer

**Type:** Incident review · INC-2026-07-30
**Status:** Final
**Window:** 2026-07-30 14:12–16:04 UTC
**Owner:** Platform
**Severity:** SEV-1

For 1 hour 52 minutes, a saturated queue turned local backpressure into a
platform-wide halt. Consumer scaling restored service; it did not remove the
failure mode.

## Impact at a glance

- Producer disruption: **1 hour 52 minutes**.
- Peak warehouse lag: **118 minutes**.
- Affected producer domains: **Checkout, Catalog, Inventory**.
- No event corruption; acceptance and freshness were unavailable.

Evidence: pager timestamps, gateway 5xx, queue depth, and warehouse freshness.

## Timeline

- **14:12** — lag crossed 120 seconds for five minutes; page fired.
- **14:18** — consumers were alive, but depth rose faster than drain rate.
- **14:31** — one replica added; lag flattened briefly.
- **15:40** — gateway timeouts created hard producer failure.
- **16:04** — second scale-up drained the queue and acceptance returned.
- **17:22** — warehouse freshness fell below ten minutes; no replay gap.

## Cause, not symptom

1. A burst exceeded drain rate while one consumer recycled.
2. One queue held every producer and had no independent path.
3. Backpressure reached the gateway as timeouts and `503` responses.

Root cause: ingestion had one queue and no failure boundary. Scaling consumers
changed recovery time, not the architecture that allowed shared failure.

## Response review

What worked: on-call found the right dashboard and the documented scale command
was safe. What failed: the page described lag but not the producer blast radius,
and the five-minute threshold consumed most of the buffer.

## Actions that change the next incident

| Action | Owner | Due | Proof |
|---|---|---|---|
| Split into independently recoverable queues | Platform | 2026-09-30 | One-queue-down test |
| Page at 60 seconds with blast radius | Reliability | 2026-08-21 | Alert fixture and game day |
| Add shed counts and retry guidance | Platform | 2026-09-05 | Dashboard review |

Closure: alert and dashboard actions are verified. Architecture remains tracked
by RFC 014 until isolation passes.
