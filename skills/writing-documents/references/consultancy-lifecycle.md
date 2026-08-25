# Consultancy lifecycle

Use this only when a request spans an engagement or asks for "the project
documents". Select the smallest supported set; never generate every page by
default.

| Stage | Typical reader need | Candidate owners |
|---|---|---|
| Frame and agree | Why, scope, outcome, effort, commercial delivery boundary | discovery, proposal, estimate, project-charter, statement-of-work |
| Define | Observable need, target design, current system, decisions, interfaces, threats | requirements, design-doc, architecture, adr, spec, api-contract, threat-model |
| Plan and govern | Work, dependencies, quality, exposure, status, controlled change | delivery-plan, test-strategy, risk-register, status-report, change-request |
| Verify and transition | Readiness, test verdict, cutover, release impact, support and handoff | readiness-review, test-report, migration-plan, release-notes, support-model, handoff |
| Operate and improve | Find truth, execute safely, communicate incidents, learn | service-docs, reference, how-to, runbook, incident-update, postmortem, onboarding |

## Ownership rules

- The charter owns governance and success; the statement of work owns supplied
  deliverables and acceptance; the delivery plan owns current forecast.
- Requirements own observable need; design documents own proposed choices;
  architecture owns current state; ADRs own individual accepted decisions.
- Test strategy owns intended evidence; test report owns a named build's result;
  readiness review owns the go-live verdict.
- Risk register owns the full RAID ledger; status reports summarize movement and
  decisions rather than copying it.
- Migration plan owns sequence and gates; runbooks own executable steps.
- Release notes tell affected readers what changed; incident updates communicate
  live state; postmortems establish later causal learning.

Link across owners. Do not duplicate a fact to make every document standalone.
