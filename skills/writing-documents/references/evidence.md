# Evidence

Claims a reader might want to check need a state. Guessing from a filename is not evidence.

## States

| State | Meaning | Treatment |
|---|---|---|
| Verified | Directly established by current source or configuration | State as fact and cite a repo-relative path |
| Provided | Business context supplied by the user or a stakeholder | Attribute it; do not use it to prove runtime |
| Inferred | Strongly suggested by several facts but not explicit | Label the inference and list supporting evidence |
| Unresolved | Conflicting or missing evidence | Put in `Open questions`; do not choose an answer |
| Recommended | A proposed improvement, not current behaviour | Keep separate from current-state documentation |

Prefer repository-relative paths. Do not cite local absolute paths.

Distinguish:

- an explicit ADR or comment explaining intent (Verified rationale)
- a repeated implementation pattern (Inferred)
- a generic industry practice that is not evidence of *this* project (Recommended, if useful)

User answers can establish intended purpose, audience, ownership, terminology, or expectations as Provided. They cannot establish that a flow, endpoint, retry, or deploy behaviour exists. Cross-check those against implementation evidence.

## Optional business-context checkpoint

After inspecting the repository, if purpose, audience, ownership, or criticality would change the document and cannot be derived from source, offer a short optional checkpoint:

- At most five questions. Every question skippable.
- Do not block writing on unanswered items.
- Record answers as Provided. Leave unanswered material as Open questions, or omit the unsupported claim.

Do not ask the user to restate facts already in the repository.

## Privacy

Never include:

- passwords, tokens, API keys, client secrets, signing material
- private keys, certificates, keystore contents
- decrypted secure properties or ciphertext copied as an example
- real customer payloads, log bodies, personal information
- private hostnames, tenant IDs, usernames, or emails unless the user has asked for a private internal document and the value is necessary
- local filesystem paths from a developer machine

Document configuration as keys and placeholders (`${PROPERTY_KEY}`, `api.example.invalid`, `<redacted>`). Describe authentication at the mechanism level.

In reusable examples (this skill, this repo's gallery) use only neutral identities. In documentation generated *for the current project*, keep real non-secret system names unless the user asks to anonymise.

## Pre-delivery

- Search the output for credentials, bearer tokens, private keys, ciphertext.
- Search for local absolute paths, emails, private domains.
- Confirm inferred claims are labelled and recommendations are not written as current behaviour.
- Confirm sample payloads are synthetic and minimal.
