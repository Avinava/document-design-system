# MuleSoft suite

```yaml
slug: mulesoft
title: MuleSoft project documentation
aliases: [mule, mule-docs]
example: examples/mulesoft.html
command: /document-design-system:mulesoft
default-format: markdown
path: docs/
```

**Reader's question:** what does this Mule application do, how does a request move, how does it fail, and how does another engineer operate or extend it?

This is a **suite**, not a single file. Shapes come from [mule-docs](https://github.com/Avinava/mule-skills/tree/main/skills/mule-docs) blueprints. This type does not copy that skill's inventory scripts.

## When to use

The repo is a Mule app (`mule-artifact.json`, `src/main/mule`, or mule packaging).

If the `mule-docs` skill is installed and the user asked for Markdown documentation of a Mule project, **prefer mule-docs** (inventory + evidence). Use this type when mule-docs is absent, or when they asked for designed HTML of the suite.

When not: generic non-Mule repositories. When not: generating Mule XML or running MUnit.

## Adaptive set

| Evidence | Document |
|---|---|
| Valid Mule project | README + `docs/architecture.md` (`architecture`) |
| RAML/OAS, APIKit, or HTTP listeners | `docs/api-contract.md` (`api-contract`) |
| Reproducible setup | `docs/onboarding.md` (`onboarding`) |
| Schedulers, queues, batch, retries, monitoring | `docs/operations.md` (runbook-adjacent; current behaviour only) |
| More than ten top-level flows | `docs/flows.md` |

Do not create an empty file. Apply `evidence.md` states on every claim. Never invent Anypoint topology, never paste secrets, never copy another customer's flows.

## Evidence order

1. Runtime: Mule XML and DataWeave.
2. Public contract: RAML/OAS, cross-checked against listeners and APIKit.
3. Build versions: POM and mule-artifact.
4. Configuration: property *keys* and committed templates, never deployed values.
5. Tests: MUnit source and CI.
6. Existing prose: after verification.

A flow name is not proof of business purpose. An API spec is not proof every route is implemented.

## Output

Markdown in the project, always. HTML index at `examples/mulesoft.html` in *this* repo's gallery; in a user project, assemble HTML only when asked. Theme `field-notes`.
