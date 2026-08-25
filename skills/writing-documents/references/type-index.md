# Type index

Load this file when the slug is unclear. Then load **one** `type-<slug>.md`. Aliases are not filenames.

## Shipped

| Slug | Pattern | Default theme | Conventional path | Command |
|---|---|---|---|---|
| `design-doc` | decision | field-notes | `docs/design/` | `/document-design-system:design-doc` |
| `adr` | record | field-notes | `docs/adr/adr-NNN.md` | `/document-design-system:adr` |
| `spec` | contract | field-notes | `docs/spec/` | `/document-design-system:spec` |
| `api-contract` | contract | console-violet | `docs/api.md` | `/document-design-system:api-contract` |
| `architecture` | system | field-notes | `docs/architecture.md` | `/document-design-system:architecture` |
| `handoff` | procedure | field-notes | `docs/handoff.md` | `/document-design-system:handoff` |
| `design-handoff` | system | editorial-coral | `docs/design-handoff.md` | `/document-design-system:design-handoff` |
| `discovery` | decision | field-notes | `docs/discovery.md` | `/document-design-system:discovery` |
| `test-report` | contract | editorial-coral | `docs/test-reports/` | `/document-design-system:test-report` |
| `postmortem` | incident | console-violet | `docs/postmortems/` | `/document-design-system:postmortem` |
| `proposal` | decision | executive-navy | `docs/proposals/` | `/document-design-system:proposal` |
| `runbook` | procedure | console-violet | `docs/runbooks/` | `/document-design-system:runbook` |
| `onboarding` | learning | field-notes | `docs/onboarding.md` | `/document-design-system:onboarding` |
| `tutorial` | learning | editorial-coral | `docs/tutorials/` | `/document-design-system:tutorial` |
| `how-to` | procedure | editorial-coral | `docs/how-to/` | `/document-design-system:how-to` |
| `reference` | contract | console-violet | `docs/reference/` | `/document-design-system:reference` |
| `explanation` | learning | field-notes | `docs/explanation/` | `/document-design-system:explanation` |
| `mulesoft` | suite | field-notes | `docs/` (suite) | `/document-design-system:mulesoft` |

Aliases remain in the individual type files. Pattern defaults are structural;
themes can change with audience without changing the type.

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
