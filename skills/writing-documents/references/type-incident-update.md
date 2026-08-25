# Incident update

```yaml
slug: incident-update
title: Incident update
aliases: [incident-comms, service-status-update, outage-update]
example: examples/incident-update.html
command: /document-design-system:incident-update
pattern: brief
default-theme: console-violet
default-format: markdown
path: docs/incidents/updates/
```

**Reader's question:** what is happening now, who is affected, and when is the next update?

Lead with severity, status, start time, current impact, and next update time.
Then state known facts, mitigation underway, what users/operators should do,
uncertainties, and a short timestamped update history.

Do not speculate about cause or blame during response. The later causal record
is `postmortem`; the operator procedure is `runbook`. Update stale statements
rather than silently leaving them current.

## Output

Markdown in `docs/incidents/updates/`; pattern `brief`, theme `console-violet`.
