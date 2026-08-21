# Discovery

```yaml
slug: discovery
title: Discovery brief
aliases: [design-discovery, research-synthesis]
example: examples/discovery.html
command: /document-design-system:discovery
default-format: markdown
path: docs/discovery.md
```

**Reader's question:** what did we learn, what is still assumed, and should we proceed?

Shape after [GOV.UK discovery](https://www.gov.uk/service-manual/agile-delivery/how-the-discovery-phase-works) and Teresa Torres' opportunity solution tree (outcome → opportunities → solutions → experiments).

## When to use

Before committing to build. The document must enable go / stop / reframe.

When not: a PRD. A PRD says what to build; discovery says whether and why. Until `prd` exists, a defined ask is `proposal` + `spec`. When not: a design-doc for an already-chosen approach.

## Sections

| Section | Content |
|---|---|
| Goal of this discovery | Decision it must enable (go to alpha / stop / reframe) |
| Problem as reframed | Not the requested solution |
| Users and context | What they are trying to do; wider journey |
| Evidence | Interviews, analytics, support tickets — counted, dated, method |
| Opportunities | Outcome-linked; not a feature list |
| Constraints | Hard vs soft (legislation, legacy, contracts) |
| Alternatives to building | Content, process, partner, do nothing |
| Assumptions still open | Ranked by risk |
| Recommendation | Proceed / stop / reframe, with the cost of being wrong |
| What would be tested next | If proceeding |

## Evidence

Distinguish **Provided** stakeholder goals from **Verified** research. Count the interviews. "Users said" without a count is not evidence.

Figures: journey and opportunity tree via `diagram-design`.

## Failure modes

A PRD in disguise. Solutions before opportunities. Uncounted "users said". Skipping "stop" as a valid output.

## Output

Markdown at `docs/discovery.md`. HTML when the brief leaves git. Theme `field-notes`.
