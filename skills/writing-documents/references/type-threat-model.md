# Threat model

```yaml
slug: threat-model
title: Threat model
aliases: [security-review, threat-assessment, security-design-review]
example: examples/threat-model.html
command: /document-design-system:threat-model
pattern: assurance
default-theme: console-violet
default-format: markdown
path: docs/security/threat-model.md
```

**Reader's question:** what can go wrong, what will we do, and is the remaining risk accepted?

Lead with an explicit accept, mitigate, or block verdict on the residual risk,
before the detail. Use the methodology-neutral four questions from the
[OWASP Threat Modeling Project](https://owasp.org/www-project-threat-modeling/):
what are we working on, what can go wrong, what will we do, and did we do a
good enough job?

## Sections

Verdict (accept, mitigate, or block), stated first; scope and assumptions;
system/data-flow model and trust boundaries; assets and actors; threats with
stable IDs; likelihood/impact method; controls and owners; validation
evidence; residual risk and explicit acceptance; review triggers.

Do not paste secrets, claim a control exists without evidence, or treat one
method such as STRIDE as universally required.

## Output

Markdown at `docs/security/threat-model.md`; pattern `assurance`, theme
`console-violet`.
