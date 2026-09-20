# Type index

Load this file when the requested name is unclear. Route to one canonical
reader job, then load exactly one `type-<slug>.md`. Aliases are not filenames or
duplicate slash commands.

## Canonical catalog

| Slug | Pattern | Default theme | Conventional path |
|---|---|---|---|
| `design-doc` | decision | field-notes | `docs/design/` |
| `discovery` | decision | field-notes | `docs/discovery.md` |
| `proposal` | decision | executive-navy | `docs/proposals/` |
| `project-charter` | decision | executive-navy | `docs/project-charter.md` |
| `estimate` | decision | executive-navy | `docs/estimates/` |
| `change-request` | decision | executive-navy | `docs/changes/` |
| `adr` | record | field-notes | `docs/adr/adr-NNN.md` |
| `spec` | contract | field-notes | `docs/spec/` |
| `api-contract` | contract | console-violet | `docs/api.md` |
| `reference` | contract | console-violet | `docs/reference/` |
| `requirements` | contract | field-notes | `docs/requirements/` |
| `statement-of-work` | contract | executive-navy | `docs/statement-of-work.md` |
| `support-model` | contract | field-notes | `docs/support-model.md` |
| `handoff` | procedure | field-notes | `docs/handoff.md` |
| `how-to` | procedure | editorial-coral | `docs/how-to/` |
| `runbook` | procedure | console-violet | `docs/runbooks/` |
| `explanation` | learning | field-notes | `docs/explanation/` |
| `onboarding` | learning | field-notes | `docs/onboarding.md` |
| `tutorial` | learning | editorial-coral | `docs/tutorials/` |
| `architecture` | system | field-notes | `docs/architecture.md` |
| `design-handoff` | system | editorial-coral | `docs/design-handoff.md` |
| `postmortem` | incident | console-violet | `docs/postmortems/` |
| `service-docs` | suite | field-notes | `docs/` |
| `delivery-plan` | plan | executive-navy | `docs/delivery-plan.md` |
| `migration-plan` | plan | console-violet | `docs/migration-plan.md` |
| `test-strategy` | plan | editorial-coral | `docs/test-strategy.md` |
| `test-report` | assurance | editorial-coral | `docs/test-reports/` |
| `threat-model` | assurance | console-violet | `docs/security/threat-model.md` |
| `readiness-review` | assurance | console-violet | `docs/readiness/` |
| `risk-register` | assurance | executive-navy | `docs/risk-register.md` |
| `status-report` | brief | executive-navy | `docs/status/` |
| `release-notes` | brief | editorial-coral | `docs/releases/` |
| `workshop-summary` | brief | field-notes | `docs/workshops/` |
| `incident-update` | brief | console-violet | `docs/incidents/updates/` |

Every canonical command is `/document-design-system:<slug>`.

## Common consultancy names

- TDD, technical design, solution design, proposed HLD → `design-doc`.
- Current-state HLD, system architecture → `architecture`.
- LLD, technical spec, protocol or interface spec → `spec`.
- PRD, BRD, FRD, SRS, functional requirements → `requirements`.
- API spec, OpenAPI, RAML, AsyncAPI → keep the machine file authoritative;
  use `api-contract` for its human companion and `spec` for normative prose.
- Project plan, implementation plan, roadmap → `delivery-plan`.
- Cutover, data migration, decommission → `migration-plan`.
- Test plan, QA strategy → `test-strategy`; named build sign-off → `test-report`.
- Security review → `threat-model`; PRR/ORR/go-live review → `readiness-review`.
- RAID, risk or issue log → `risk-register`; high-volume data may belong in a tracker.
- Weekly report or steering update → `status-report`.
- Service handbook or application documentation → `service-docs`.
- Scope change or variation → `change-request`.
- Formal meeting/workshop readout → `workshop-summary`; casual note edits stay casual.

## Compatibility profile

`/document-design-system:mulesoft` remains supported. It loads
`type-service-docs.md` plus `profile-mulesoft.md`; it is not a second canonical
type.

## Routing boundaries

- A proposed architecture is `design-doc`; current state is `architecture`.
- Machine API/schema files remain source of truth; this skill does not fabricate
  an OpenAPI, RAML, AsyncAPI, or JSON Schema when asked only for prose docs.
- Metric-led reports route to `analytical-document-design`; slides route to
  `presentation-design`.
- MSAs, NDAs, invoices, procurement, HR, and invented legal clauses are out of
  scope. `statement-of-work` covers supplied delivery-commercial terms only.
- If several reader jobs apply, use `consultancy-lifecycle.md` and `suites.md`.
