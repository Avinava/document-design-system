# Runbook

```yaml
slug: runbook
title: Runbook
aliases: [playbook]
example: examples/runbook.html
command: /document-design-system:runbook
default-format: markdown
path: docs/runbooks/
```

**Reader's question:** what do I do right now?

## When to use

An incident or operational procedure someone tired will follow at 3am. A checklist.

When not: explaining why the system is this way — link a `design-doc` or `adr`. When not: first-day setup (onboarding, when that type ships).

## Sections

| Section | Content |
|---|---|
| When to use | The symptom or trigger |
| Preconditions | Access, tools, state required before starting |
| Steps | Numbered, imperative, individually verifiable |
| Verification | How to confirm it worked |
| Rollback | How to undo it |
| Escalation | Who to contact, and when to stop trying |

## Notes

- Written for someone tired, at 3am, who did not write the system. Assume no context.
- Every step is one action, and says how to tell it succeeded.
- Include the actual commands, copy-pasteable, with placeholders clearly marked.
- Say what to do when a step fails — that is when the runbook is actually being read.
- Date the runbook and name its owner. Stale runbooks are worse than none, because they are followed.

## Failure modes

Prose. A runbook is a checklist. Anything explanatory goes in a linked design doc, not inline where it slows down someone in an incident.

## Output

Markdown in `docs/runbooks/`. HTML when printed for a war room; theme `console-violet`.
