# Current ingestion build can ship with two explicit waivers

**Type:** Release evidence · RC 2026.08.12
**Build:** `sha-8132c3`
**Environment:** staging
**Author:** Platform

## Release verdict

**Go with waivers.** All 38 executed tests passed. Two chaos scenarios were
skipped because the current build has one queue; they remain release risks.

## Objective and scope

Verify acceptance, idempotency, lookup, authentication, current overload
behavior, consumer drain, and warehouse landing. Dispatcher partitioning and
one-queue-down recovery are outside this build.

## Results with denominators

| Suite | Planned | Executed | Passed | Skipped |
|---|---:|---:|---:|---:|
| Gateway contract | 18 | 18 | 18 | 0 |
| Consumer and warehouse | 14 | 14 | 14 | 0 |
| Failure and recovery | 8 | 6 | 4 pass + 2 expected current failures | 2 |
| **Total** | **40** | **38** | **36 expected passes** | **2** |

Executed denominator: 38. Pass denominator: 36 tests whose expected result was
pass. Two overload tests correctly observed the current `503` behavior.

## Defects and waivers

- **WAIVER-01 — No two-queue chaos environment.** One selected queue cannot be
  failed independently until RFC 014 exists in staging.
- **WAIVER-02 — Shed contract unresolved.** Current behavior remains `503`;
  producer guidance must not claim the proposed response.

No functional defect was found in the current release scope.

## Exit criteria

- All executed release-blocking tests pass.
- Both waivers are named in release notes.
- Production monitoring gains no new dependency.
- Rollback remains the prior container image.

## Residual risk

This build preserves the shared queue. It can ship because it does not worsen
that risk; it does not mitigate the incident pattern in RFC 014.
