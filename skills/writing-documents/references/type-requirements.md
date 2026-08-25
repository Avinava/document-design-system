# Requirements

```yaml
slug: requirements
title: Requirements specification
aliases: [prd, brd, frd, srs, functional-spec, requirements-spec]
example: examples/requirements.html
command: /document-design-system:requirements
pattern: contract
default-theme: field-notes
default-format: markdown
path: docs/requirements/
```

**Reader's question:** what outcome and observable behavior must delivery satisfy?

Use for an agreed, traceable requirement set after discovery. Follow the
lifecycle-aware information model in
[ISO/IEC/IEEE 29148](https://www.iso.org/standard/72089.html) without copying a
standard template blindly.

## Sections

Purpose and users; scope and non-scope; definitions; assumptions and
dependencies; functional requirements with stable IDs; quality attributes and
constraints; acceptance measures; traceability; unresolved decisions.

Requirements state observable need, not implementation preference. Link design
choices to `design-doc` and interfaces to their machine definitions or
`api-contract`.

## Output

Markdown in `docs/requirements/`; pattern `contract`, theme `field-notes`.
