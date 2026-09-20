# MuleSoft service-docs profile

Load this only when the user invokes `/document-design-system:mulesoft` or the
repository is clearly a Mule application. The canonical suite is
[`type-service-docs.md`](type-service-docs.md); this profile specializes its
evidence sources without changing its document ownership rules.

If the `mule-docs` skill is installed and the user asked for Markdown
documentation of a Mule project, prefer that skill's inventory-and-evidence
workflow. Use this profile when `mule-docs` is absent, or when the user asked
for designed HTML of the suite.

- Treat RAML, Mule configuration, properties, deployment descriptors, and
  MUnit results as primary evidence.
- Map listeners, flows, transforms, error handlers, retry/dead-letter behavior,
  and downstream calls into the generic architecture and contract pages.
- Never infer an environment, public hostname, passing test, or secret value.
- Emit only supported pages. Do not create empty runbook or test-report stubs.

## Where the old adaptive pages went

| Pre-0.3 output | Current home |
|---|---|
| `docs/operations.md` (schedulers, queues, batch, retries, monitoring; current-behavior only) | Fold into `docs/architecture.md` as the current operational-behavior section |
| `docs/flows.md` (more than ten top-level flows) | Fold into `docs/architecture.md` as a flow inventory; use `docs/api-contract.md` instead for flows that are public API routes |

The compatibility command remains supported, but new general service
documentation requests route to `service-docs`.
