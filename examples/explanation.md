# Why ingestion fails as a whole even when only one component is full

**Type:** Conceptual explanation
**Question:** why does local backpressure become a platform halt?
**Scope:** current architecture

The important property is not queue size. It is the absence of an independent
path: every producer and consumer shares the same place where work can wait.

## One queue creates one fate

Checkout, Catalog, and Inventory enter through the same gateway and wait on the
same queue. Their volumes differ, but their ability to make progress does not:
when the queue cannot accept, the gateway has nowhere else to place any event.

Shared infrastructure becomes shared fate when it has no independent failure
or recovery boundary.

## Capacity changes the clock, not the topology

A larger queue or more default consumers can absorb a bigger burst. If
saturation still arrives, every producer remains behind it.

Independent queues change who can continue. One partition can fail while the
other accepts, even if total capacity stays constant.

## Backpressure travels upstream

1. Consumers slow and drain rate falls below arrival rate.
2. The queue fills and stops accepting within the gateway wait budget.
3. The gateway blocks or returns overload to every caller.

The July incident followed this chain. Scaling consumers increased drain rate
and recovered the queue; it did not prevent recurrence.

## Degradation is a defined leftover

Under RFC 014, a failed queue leaves the other partition accepting events,
bounds gateway wait, records a shed outcome, and tells producers to retry the
same event ID.

The proposal is useful because it defines what continues, what stops, and how
callers recover. “More resilience” alone does not.
