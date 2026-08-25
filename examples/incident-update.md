# P1 ingestion delay affects Checkout, Catalog, and Inventory

**Status:** Investigating<br>
**Started:** 2026-07-30 14:12 UTC<br>
**This update:** 14:31 UTC<br>
**Next update:** 14:45 UTC

## Current impact

Event acceptance is returning `503` or blocking for Checkout, Catalog, and
Inventory. Warehouse freshness is rising. Cause is not yet known.

## Mitigation underway

Platform is adding one consumer replica and will observe lag for three minutes.
No queue will be deleted and replica count will not exceed six without
Reliability.

## What users should do

Producers should retain bounded retry behavior and preserve event IDs. After
15 minutes without falling lag, or on any crash loop, Platform pages
Reliability and stops replica changes.

This is a live update, not the later postmortem.
