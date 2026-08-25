# Three delivery exposures need owners before staging dual-write

**Review:** 2026-08-26<br>
**Overall:** High exposure<br>
**Next review:** 2026-09-02

## Rating method

Exposure is written as Low, Medium, or High using likelihood and delivery
impact. Color is supplementary.

## RAID register

| ID | Type | Statement | Exposure | Owner | Due | Movement |
|---|---|---|---|---|---|---|
| RAID-01 | Risk | Chaos environment misses gate | High | Platform | 2026-09-18 | New |
| RAID-02 | Decision | Shed response unresolved | High | Reliability | 2026-09-01 | Unchanged |
| RAID-03 | Dependency | Producer retry fixtures | Medium | Producer teams | 2026-10-16 | New |

## Treatment

Platform confirms an environment plan weekly. Reliability decides RAID-02.
Checkout, Catalog, and Inventory each own one retry fixture. Status reports
summarize movement and link here rather than copying the register.
