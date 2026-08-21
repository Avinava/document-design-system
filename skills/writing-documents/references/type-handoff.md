# Handoff

```yaml
slug: handoff
title: Engineering handoff
aliases: [engineering-handoff, knowledge-transfer]
example: examples/handoff.html
command: /document-design-system:handoff
default-format: markdown
path: docs/handoff.md
```

**Reader's question:** what do I need to run, change, and not break this after you leave?

Shape after project handover and knowledge-transfer checklists ([Smartsheet](https://www.smartsheet.com/content/project-handover-templates), [Enboarder](https://enboarder.com/blog/checklist-knowledge-transfer/)).

## When to use

Work is transferring between engineers, from a contractor to a client team, or at the end of an engagement.

When not: a first-day setup guide with no in-flight work — that is `onboarding`. When not: a design-to-dev packet of screens and states — that is `design-handoff`.

## Sections

| Section | Content |
|---|---|
| Scope and date | What is being handed, as-of date, outgoing and incoming owners |
| What it is | One paragraph + link to architecture / README |
| Current status | In-flight work, open PRs, unreleased branches, known bugs |
| How to run it | Commands that actually work in this repo (from CI/Makefile/POM) |
| Where truth lives | Code, configs, dashboards, secrets *locations* (not values), vendor contacts |
| Decisions that bind | Links to ADRs / design docs; verbal decisions written down now |
| Risks and tripwires | What will page, what is fragile, what looks fine and is not |
| Access and accounts | Named systems to request; no credentials |
| First-week checklist | Ordered, verifiable |
| Open questions | Owner + date |

## Evidence to inspect

README, CI, ADRs, open issues, `TODO`/`FIXME`, deploy workflows. Do not paste secret values.

## Failure modes

A README restated. Secrets pasted. "The code is the documentation." No in-flight work listed.

## Output

Markdown at `docs/handoff.md` or in the PR description. HTML when emailed or printed. Theme `field-notes`.
