# Test report

```yaml
slug: test-report
title: Test report
aliases: [qa-report, test-results, qa-signoff]
example: examples/test-report.html
command: /document-design-system:test-report
default-format: markdown
path: docs/test-reports/
```

**Reader's question:** can we ship, on this build, and what risk remains?

A **point-in-time results report**, not a living test inventory. Shape after [TestRail's agile test summary](https://www.testrail.com/blog/test-summary-report/).

## When to use

A go/no-go after a test cycle, sprint, or release candidate. Audits, customer sign-off, contractual evidence.

When not: a reconciled quality dashboard over time — that is `analytical-document-design`. When not: a test strategy that outlives one build.

## Sections

| Section | Content |
|---|---|
| Identity | Product, build SHA / version, environment, date, author |
| Objective and scope | In / out of scope; types of testing |
| Verdict | Go / no-go / go-with-waivers, in the first screenful |
| Results | Planned, executed, passed, failed, blocked, skipped — with denominators |
| Defects | Open by severity; links; waivers |
| Environment | Build, OS/browser/runtime matrix; no credentials or private URLs |
| Exit criteria | Met / not met / waived, each |
| Residual risk | What was not tested and why that matters |
| Appendix | Suite list or CI job links |

## Failure modes

Pass-rate without counts. Coverage % as quality. Mixing strategy with results. Environment secrets. No verdict.

Charts of pass/fail by suite come from `chart-design`.

## Output

Markdown in `docs/test-reports/`. HTML/PDF when the sign-off is emailed; `data-layout="contract"`. Theme `editorial-coral`.
