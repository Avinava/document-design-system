# Postmortem

```yaml
slug: postmortem
title: Postmortem
aliases: [incident-report, rca]
example: examples/postmortem.html
command: /document-design-system:postmortem
default-format: markdown
path: docs/postmortems/
```

**Reader's question:** what happened, why, and what stops it recurring?

## When to use

After an incident, once the immediate response is over. Blameless by default.

When not: customer-facing incident comms during the event (reserved `incident-comms`). When not: a runbook written in hindsight — extract the 3am path into `runbook`.

## Sections

| Section | Content |
|---|---|
| Summary | What broke, for how long, affecting whom |
| Impact | Quantified — users, requests, revenue, duration |
| Timeline | Detection through resolution, with timestamps and timezone |
| Root cause | The technical chain, followed to the end |
| Contributing factors | What made it worse, slower to detect, or harder to fix |
| What went well | Genuinely — this is how good practice gets reinforced |
| Action items | Owner, priority, tracking link, each |

## Notes

- **Blameless.** Name systems and processes, not people. "The deploy did not have a staging gate," not "X deployed without testing."
- **Timestamps with a timezone.** A timeline in unlabelled local time is unusable.
- Include detection time separately from resolution time. Slow detection is usually the more actionable problem.
- Action items without owners do not happen. Action items without tracking links are not tracked.

## Failure modes

Stopping at the first plausible cause. "The disk filled up" is not a root cause — why was there no alert, why did it fill, why did the service fail hard rather than degrade?

## Output

Markdown in `docs/postmortems/`. HTML when sharing beyond git; theme `console-violet`.
