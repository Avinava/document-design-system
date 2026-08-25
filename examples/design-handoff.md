# Show whether ingestion is healthy without requiring dashboard archaeology

**Type:** Design handoff · operator overview
**For:** Platform UI
**File:** operator-overview
**As of:** 2026-08-18
**Owner:** Platform

Build a read-only overview that names state, exposes queue lag and shed
behavior, and routes operators to the existing runbook.

## Primary user flow

1. Open the overview from the on-call page.
2. Read global written status and refresh time.
3. Identify the queue with rising lag or shed count.
4. Open the existing runbook; do not operate from this page.

## Screen anatomy

- **Global status:** written state, environment, refresh time, incident link.
- **Queue cards:** lag, depth, shed count, last event, written trend.
- **Next action:** one runbook link, no inline control.

## Required states

| State | Required treatment |
|---|---|
| Happy | Written healthy status with all values |
| Idle | Explain that zero traffic is not failure |
| Loading | Reserve layout; do not present stale values as current |
| Partial data | Show available queues and name missing source |
| Error | Written failure, last known update, retry, runbook |
| Recovered | Success label and recovery time, no celebration animation |

## Components and interaction

| Component | Use | Do not add |
|---|---|---|
| Status banner | Global state, environment, refresh time | Color-only state |
| Queue card | Lag, depth, shed, last event, trend | Hidden hover facts |
| Runbook link | Primary recovery action | Operational controls |
| Incident link | Active incident only | Automatic incident creation |

Refresh every 15 seconds. Preserve focus. Tab order is global status, queue
cards, runbook, then incident link.

## Responsive, content, and accessibility rules

- Two queue columns on desktop; one column on mobile in the same order.
- Never truncate names, labels, timestamps, or errors.
- Announce status changes politely, not every unchanged refresh.
- Meet AA contrast and keep visible focus.
- Use real headings and lists.

Acceptance: all six states render at 390 and 1440 pixels, status survives
grayscale, keyboard order is stable, and every failure exposes the runbook.
