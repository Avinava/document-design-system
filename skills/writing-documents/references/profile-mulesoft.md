# MuleSoft service-docs profile

Load this only when the user invokes `/document-design-system:mulesoft` or the
repository is clearly a Mule application. The canonical suite is
[`type-service-docs.md`](type-service-docs.md); this profile specializes its
evidence sources without changing its document ownership rules.

- Treat RAML, Mule configuration, properties, deployment descriptors, and
  MUnit results as primary evidence.
- Map listeners, flows, transforms, error handlers, retry/dead-letter behavior,
  and downstream calls into the generic architecture and contract pages.
- Never infer an environment, public hostname, passing test, or secret value.
- Emit only supported pages. Do not create empty runbook or test-report stubs.

The compatibility command remains supported, but new general service
documentation requests route to `service-docs`.
