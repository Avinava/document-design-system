# Type index

Load this file when the requested name is unclear. Route by the reader's
question: if a type or alias fits, load its `type-<slug>.md`; if none fits,
pick the pattern from the table below and compose with `composing.md`. Aliases
are not filenames or duplicate slash commands.

## Start from the reader's question

| The reader asks | Pattern | Presets in that pattern |
|---|---|---|
| Should we do this, and what do you need from me? | `decision` | `design-doc`, `discovery`, `proposal`, `project-charter`, `estimate`, `change-request` |
| Why is it like this, and is that settled? | `record` | `adr` |
| What exactly must be true, and how do I check it? | `contract` | `spec`, `api-contract`, `reference`, `requirements`, `statement-of-work`, `support-model` |
| What do I do, in what order, and how do I recover? | `procedure` | `handoff`, `how-to`, `runbook` |
| How does this work, so I can reason about it myself? | `learning` | `explanation`, `onboarding`, `tutorial` |
| How is it arranged, and where are the boundaries? | `system` | `architecture`, `design-handoff` |
| What happened, why, and what stops it recurring? | `incident` | `postmortem` |
| Where is each fact about this service owned? | `suite` | `service-docs` |
| How will the work get done, and what gates it? | `plan` | `delivery-plan`, `migration-plan`, `test-strategy` |
| Is it good enough, on what evidence? | `assurance` | `test-report`, `threat-model`, `readiness-review`, `risk-register` |
| Where are we now, and what needs my attention? | `brief` | `status-report`, `release-notes`, `workshop-summary`, `incident-update` |

When the question matches a row but none of its presets match the reader or the
document's job — a primer for engineers arriving from another discipline, a
glossary-led orientation, a comparison of two internal platforms — compose in
that pattern with `composing.md` rather than forcing the nearest preset.

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
- Solution architecture document, integration design, target-state design →
  `design-doc`; as-built or current-state integration landscape → `architecture`.
- Interface agreement, interface control document, integration contract → `spec`.
- Business case, investment paper, funding request → `proposal`.
- Inception or discovery readout, current-state assessment → `discovery`.
- Rough order of magnitude, sizing → `estimate`.
- Knowledge-transfer pack, operational handover → `handoff`.
- Cutover plan, cutover runbook, rollback plan → `migration-plan`; the minute-by-minute
  operator steps inside it → `runbook`.
- Go/no-go, launch readiness, operational acceptance → `readiness-review`.
- Steering pack, programme update, RAG report → `status-report`.
- UAT plan → `test-strategy`; UAT sign-off or test summary report → `test-report`.
- Service catalogue entry, SLA/OLA description → `support-model`.
- Lessons learned, incident review → `postmortem`; live incident comms → `incident-update`.
- Primer, orientation guide, concept guide → `explanation` if it explains one
  system's why; compose in `learning` when the reader's starting world matters
  (see `composing.md`).

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
- A request no type or alias fits is composed (`composing.md`), not refused and
  not forced into the nearest preset. The out-of-scope list above still applies
  to composed documents.
