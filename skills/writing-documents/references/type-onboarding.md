# Onboarding

```yaml
slug: onboarding
title: Onboarding
aliases: [getting-started]
example: examples/onboarding.html
command: /document-design-system:onboarding
default-format: markdown
path: docs/onboarding.md
```

**Reader's question:** how do I get this running on my machine and prove it works?

## When to use

A new engineer, first day. Setup, not incident response.

When not: a 3am procedure — that is `runbook`. When not: transferring in-flight ownership — that is `handoff`. When not: a lesson that teaches the domain — that is `tutorial`.

## Sections

| Section | Content |
|---|---|
| Prerequisites | Tools, runtime, access. Proven by the repo, not guessed |
| Safe configuration | Property names and placeholders, never values |
| Local commands | Build, lint, test, run — from Makefile, POM, or CI |
| External systems | Only when the project contains enough evidence |
| Deployment | Steps and runtime inputs from committed automation |
| Validation | One representative transaction, as a checklist |
| Troubleshooting | Symptoms tied to actual code or configuration |

Date the document and name its owner. Stale onboarding is followed.

## Failure modes

Real usernames, private hostnames, or secret values in examples. Commands that are not in the repository. A prose tour instead of a checklist.

## Output

Markdown at `docs/onboarding.md`. Theme `field-notes` if HTML is asked for.
