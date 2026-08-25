# Repository guidance

This repository treats document design as two independent axes:

- **Document pattern** controls reading structure and is declared with
  `data-pattern`.
- **Theme** controls visual voice through semantic tokens and is declared with
  `data-theme`.

Do not reduce the writing examples to one generic longform layout. Select one
of the eleven patterns in `core/document-patterns.md`, then use the modules that
support that reader movement. Keep prose readable at 62–72 characters while
allowing maps, tables, comparisons, timelines, and registers to use the wider
shell.

Markdown in `examples/<slug>.md` is the canonical repository-friendly form.
Designed HTML is generated from `templates/types/<slug>.html`; both must use
the same title and factual anchors from `examples/WORLD.md`.

When changing a writing-document type:

1. Keep its `pattern` and `default-theme` fields aligned with
   `scripts/build_examples.py`.
2. Update both Markdown and HTML examples.
3. Rebuild with `python3 scripts/build_examples.py`.
4. Regenerate relevant screenshots with `python3 scripts/shoot_examples.py`.
5. Run `python3 -m unittest discover -s tests -v`,
   `python3 scripts/validate_repository.py .`, and
   `python3 scripts/build_site.py --check`.

Canonical consultancy aliases such as HLD, LLD, TDD, PRD, API spec, PRR, and
RAID route through `skills/writing-documents/references/type-index.md`; do not
create duplicate types or commands for a familiar filename. The `mulesoft`
command is a compatibility profile of canonical `service-docs`, not another
type.

For statements of work, estimates, and other delivery-commercial documents,
never invent parties, rates, payment terms, legal clauses, approvals, or dates.
Use the evidence states and leave missing terms unresolved.

GitHub Pages is source-built. Do not hand-edit `site/`; the workflow rebuilds
examples before assembling the deployable site.

Do not add source-provenance, copied product naming, or private reference links
to repository documents, examples, screenshots, commit messages, or release
notes. Express the design principle in this repository's own vocabulary.
