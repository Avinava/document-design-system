# Migration plan

```yaml
slug: migration-plan
title: Migration and cutover plan
aliases: [cutover-plan, data-migration-plan, decommission-plan]
example: examples/migration-plan.html
command: /document-design-system:migration-plan
pattern: plan
default-theme: console-violet
default-format: markdown
path: docs/migration-plan.md
```

**Reader's question:** how do we move from current to target safely, prove it, and back out?

## Sections

Current and target state; scope and inventory; mapping and compatibility;
preconditions; rehearsals; staged timeline; roles and communications;
validation and reconciliation; rollback trigger and steps; decommission gates;
residual risk.

The plan owns sequencing and gates. Put copy-paste execution commands in a
linked runbook. Never call a rollback viable without a tested trigger, data
position, and decision owner.

## Output

Markdown at `docs/migration-plan.md`; pattern `plan`, theme `console-violet`.
