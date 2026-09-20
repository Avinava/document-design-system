# Add event history without moving the production gate

**ID:** CR-003
**Status:** Proposed
**Decision owner:** Platform director
**Impact:** 3 engineer-weeks

## Requested change

Add a seven-day event-history panel to the operator overview.

## Baseline impact

The operator overview currently owns live status only. Accepting CR-003 adds
3 engineer-weeks. The recommended option keeps 2026-11-02 by moving the
extended onboarding lab one week after handoff.

## Options

1. Approve and move the lab: production stays 2026-11-02.
2. Approve and retain the lab: production moves one week.
3. Defer the history panel: baseline remains unchanged.

## Recommendation

Approve option 1 only after design-handoff acceptance. Until approval, RFC 014
and the 24 engineer-week estimate remain authoritative.
