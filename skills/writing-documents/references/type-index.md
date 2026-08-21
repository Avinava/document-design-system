# Type index

Load this file when the slug is unclear. Then load **one** `type-<slug>.md`. Aliases are not filenames.

## Shipped

| Slug | Aliases | Conventional path | Command |
|---|---|---|---|
| `design-doc` | rfc, tdd, technical-design, erd | `docs/design/` | `/document-design-system:design-doc` |
| `adr` | architecture-decision | `docs/adr/adr-NNN.md` | `/document-design-system:adr` |
| `spec` | specification, rfc-2119 | `docs/spec/` | `/document-design-system:spec` |
| `api-contract` | api-spec, openapi, raml-docs | `docs/api.md` | `/document-design-system:api-contract` |
| `architecture` | architecture-guide, c4 | `docs/architecture.md` | `/document-design-system:architecture` |
| `handoff` | engineering-handoff, knowledge-transfer | `docs/handoff.md` | `/document-design-system:handoff` |
| `design-handoff` | figma-handoff, dev-handoff | `docs/design-handoff.md` | `/document-design-system:design-handoff` |
| `discovery` | design-discovery, research-synthesis | `docs/discovery.md` | `/document-design-system:discovery` |
| `test-report` | qa-report, test-results, qa-signoff | `docs/test-reports/` | `/document-design-system:test-report` |
| `postmortem` | incident-report, rca | `docs/postmortems/` | `/document-design-system:postmortem` |
| `proposal` | — | `docs/proposals/` | `/document-design-system:proposal` |
| `runbook` | playbook | `docs/runbooks/` | `/document-design-system:runbook` |
| `onboarding` | getting-started | `docs/onboarding.md` | `/document-design-system:onboarding` |
| `tutorial` | lesson | `docs/tutorials/` | `/document-design-system:tutorial` |
| `how-to` | howto, how-to-guide | `docs/how-to/` | `/document-design-system:how-to` |
| `reference` | api-reference | `docs/reference/` | `/document-design-system:reference` |
| `explanation` | concept, why | `docs/explanation/` | `/document-design-system:explanation` |
| `mulesoft` | mule, mule-docs | `docs/` (suite) | `/document-design-system:mulesoft` |

Always load `type-<slug>.md` before writing.

## Routing

- Company RFC, TDD, ERD → `design-doc`. IETF / RFC 2119 normative text → `spec`.
- A request to "write the docs" with no type: ask which slug, or propose a small suite (`suites.md`). Do not emit one blob.
- Metric-led report → `analytical-document-design`. Slides → `presentation-design`.
- If two slugs both fit, split. A runbook does not carry the design argument.

## Not yet a type

Do not create files or commands for these. Route as noted.

| Reserved slug | Until then, use |
|---|---|
| `prd` | `proposal` + `spec` |
| `security-review` | `design-doc` cross-cutting section |
| `migration` | `design-doc` + `runbook` |
| `release-notes` | not a type; do not pretend |
| `incident-comms` | not `postmortem` (different audience) |
