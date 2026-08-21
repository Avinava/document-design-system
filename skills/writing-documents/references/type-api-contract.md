# API contract

```yaml
slug: api-contract
title: API contract
aliases: [api-spec, openapi, raml-docs]
example: examples/api-contract.html
command: /document-design-system:api-contract
default-format: markdown
path: docs/api.md
```

**Reader's question:** how do I call this correctly, and what happens when I do it wrong?

The machine spec (OpenAPI / RAML / AsyncAPI) is the source of truth ([OAI best practices](https://learn.openapis.org/best-practices.html)). This type owns the **companion document**, never a second copy of the spec.

## When to use

A human-readable contract next to an OAS/RAML/AsyncAPI file, or when callers need auth, errors, and examples explained in prose.

When not: rewriting the OpenAPI file. When not: a design arguing for an API shape — that is `design-doc`. When not: generated reference dumped from the spec — that is closer to `reference`.

## Sections

| Section | Content |
|---|---|
| Audience and base | Declared base path; no invented hostnames |
| Auth | Scheme at contract level; no secrets |
| Resource map | Grouped operations, one table |
| Conventions | Idempotency, pagination, correlation, versioning, error envelope |
| Worked examples | Synthetic, one success + one error per important operation |
| Error catalog | Stable codes, meaning, what the client should do |
| Spec ↔ implementation mismatches | Documented, not silently "fixed" |
| Changelog | Breaking vs additive |

## Evidence

If an OAS/RAML file exists, read it; do not rewrite it. Link it. Cross-check listeners and routes. A listener path is not proof of the public URL.

## Failure modes

Dumping the OAS. Copying production payloads. Invented hostnames. Prose and spec diverging.

## Output

Markdown at `docs/api.md`. HTML when sharing with non-git readers; `data-layout="contract"`. Theme `console-violet`.
