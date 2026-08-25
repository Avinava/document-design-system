# Queue isolation is agreed; shed behavior and chaos ownership remain open

**Workshop:** 2026-08-18<br>
**Purpose:** Confirm RFC 014 target outcome<br>
**Facilitator:** Platform

## What the evidence established

Four of six incidents share the queue boundary. Alert tuning shortens detection
but does not prevent a platform-wide halt.

## Agreements

- Queue isolation is the target outcome.
- Producer payload, authentication, warehouse schema, batch path, and retention
  stay outside scope.
- One queue down must leave the other accepting events.

## Open questions and actions

Reliability decides shed response under RAID-02 by 2026-09-01. Platform names
the chaos environment owner and confirms 2026-09-18. Producer teams supply
retry fixtures by 2026-10-16.

These agreements feed requirements and RFC 014; this page does not replace them.
