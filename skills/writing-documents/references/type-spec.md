# Specification

```yaml
slug: spec
title: Specification
aliases: [specification, rfc-2119]
example: examples/spec.html
command: /document-design-system:spec
default-format: markdown
path: docs/spec/
```

**Reader's question:** what exactly must I build, and how do I know I am done?

## When to use

Normative requirements that bind an implementer. IETF-style RFCs, protocol specs, internal MUST/SHOULD/MAY documents.

When not: a design arguing for an approach — that is `design-doc`. When not: a human-readable API companion next to OpenAPI — that is not this type until `api-contract` ships; until then, keep the machine spec as the source of truth and write a short companion as `spec` only if it is genuinely normative.

## Sections

| Section | Content |
|---|---|
| Scope | What this specifies, and what it does not |
| Definitions | Terms with precise meanings, referenced throughout |
| Requirements | Normative statements, individually identified |
| Examples | Concrete cases, including edge cases |
| Compliance | How conformance is determined |

## Notes

- Use RFC 2119 keywords (MUST, SHOULD, MAY) and say at the top that you are doing so. Without that, "should" is ambiguous between a requirement and a suggestion.
- Give every requirement a stable identifier (`REQ-014`). Tests, reviews, and bug reports need something to reference, and section numbers shift.
- Examples are normative in practice, whatever the document says — implementers read them first and copy them.
- Specify error and boundary behaviour. Unspecified means every implementation differs.

## Failure modes

Mixing normative requirements with explanatory prose so an implementer cannot tell which sentences bind. Separate them visually.

## Output

Markdown in `docs/spec/`. HTML when asked; `data-layout="contract"` for table-heavy specs. Theme `field-notes`.
