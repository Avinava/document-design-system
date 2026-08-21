Design handoff

  # Ingestion status — operator view

  

    **For:** Platform UI ·
    **File:** Figma · Ingestion / status (link the file; this is the packet) ·
    **As of:** 2026-08-12
  

  
## Overview

  
Operators need to see whether ingestion is healthy without opening four dashboards. In-scope: a single status page for queue lag and shed count. Out of scope: producer configuration.

  
## User flow

  

    - Open Status.
    - See current lag and whether shed is active.
    - If lag is high, follow the runbook link.
  

  
## Screens

  

    - Happy — lag under 30s, shed count zero.
    - Empty — no events in 15 minutes. Copy: "No events in the last 15 minutes. Producers may be idle."
    - Loading — skeleton bars, no fake numbers.
    - Error — dashboard query failed. Copy: "Status unavailable. Try again, then page Platform."
    - Success — not a toast; the happy state is the success.
  

  
## Components

  
Use `StatusBanner`, `MetricCard`, `Button` from the platform system. No custom chart — a number plus a 15-minute sparkline from `Sparkline`. Do not introduce a new accent; use the system danger token for shed-active.

  
## Interaction

  
Focus order: title, lag metric, shed metric, runbook link. Keyboard: tab through; Enter on the runbook link. No motion beyond the existing 150ms fade on number change. Honour `prefers-reduced-motion`.

  
## Responsive

  
One column below 720px. Two metric cards stack; do not shrink type below 16px.

  
## Content

  
Lag label: "Queue lag". Units: seconds. Truncate shed counts with SI (1.2k), not "1200.00". Empty strings are the empty-state copy above — never blank cards.

  
## Data

  
Lag from `ingest_lag_seconds`. Shed from `dispatcher_shed_total` (zero until RFC 014 ships — show the metric, value 0, no "coming soon"). If the operator lacks the dashboard role, hide the page behind the existing 403, do not show zeros.

  
## Accessibility

  
Metric numbers have visible text, not colour-only. StatusBanner uses text + icon. Contrast already in the system; do not override.

  
## Acceptance criteria

  

    - Given lag 12s and shed 0, when I open Status, then I see 12 and 0 and no error.
    - Given the query fails, when I open Status, then I see the error copy and no invented lag.
    - Given a viewport 375px wide, when I open Status, then both metrics remain fully visible without horizontal scroll.
