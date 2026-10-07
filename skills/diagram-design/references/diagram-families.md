# Diagram families

Per-form construction rules. Each entry covers what the form is for, what to label, where the accent goes, and the failure mode that form invites.

## Contents

- [Architecture / system map](#architecture--system-map)
- [Flow](#flow)
- [Sequence](#sequence)
- [State machine](#state-machine)
- [Data model](#data-model)
- [Timeline](#timeline)
- [Swimlane](#swimlane)
- [Quadrant](#quadrant)
- [Layer stack](#layer-stack)
- [Funnel](#funnel)
- [Venn](#venn)
- [Tree / nested](#tree--nested)
- [Change view](#change-view)
- [Deployment map](#deployment-map)
- [Dependency graph](#dependency-graph)

A form earns a place in this list only when it needs a layout none of the others has. A new form for a new subject drawn in an old layout is just that old form.

---

## Architecture / system map

**For:** how parts are arranged and what talks to what.

- Group by trust boundary, deployment unit, or ownership — whichever the reader actually needs. Pick one; grouping by two things at once produces a diagram nobody can read.
- Draw boundaries as dashed `var(--rule-strong)` rectangles with a label in the top-left. A boundary without a label is decoration.
- Direction of data flow gets an arrowhead. Bidirectional links get two, or a single line with a label saying what each direction carries.
- External systems sit at the edges, visually distinct (dashed border, `var(--soft)` label).
- **Accent:** the component the diagram is about — the bottleneck, the new thing, the single point of failure.

**Failure mode:** drawing the org chart instead of the system. If two boxes exist only because two teams exist, the diagram is about people and should say so.

**Hand-author this one.** Position carries coupling.

---

## Flow

**For:** how something moves through steps, with branches.

- Left-to-right for a process, top-to-bottom for a decision cascade. Not both.
- Every decision node has labelled outgoing edges. An unlabelled branch is unreadable.
- The happy path runs straight; exceptions branch off it. A diagram where every path looks equally likely misrepresents the system.
- Terminal states are visually distinct from process steps.
- **Accent:** the failure path, or the step where the change happens.

**Failure mode:** a flowchart of a linear process. If there are no branches, write numbered steps.

---

## Sequence

**For:** who calls whom, in what order, over time.

- Participants across the top, lifelines descending. Time is the vertical axis and must stay monotonic.
- Label every message with what it carries, not just that it happens.
- Mark synchronous versus asynchronous — solid arrowhead for a call that blocks, open for one that does not.
- Show returns only when the return value matters; drawing every return doubles the lines and adds nothing.
- Activation bars only if the diagram is about timing or contention.
- **Accent:** the message that fails, retries, or times out.

**Failure mode:** more than about seven participants. Beyond that, split by phase.

**Auto-layout is fine here** — the arrangement is dictated by the protocol, not chosen. Use `scripts/render_diagram.mjs`.

---

## State machine

**For:** what states exist and what transitions between them.

- Every transition is labelled with its trigger. An unlabelled transition means the diagram does not know why it happens.
- Mark the initial state unambiguously, and every terminal state.
- Show self-transitions only when they matter (retry, refresh).
- If a state has no outgoing transition and is not terminal, that is a bug in the system or in the diagram. Resolve it before shipping.
- **Accent:** the error state, or the state the system gets stuck in.

**Failure mode:** conflating states with steps. A state persists; a step completes.

**Auto-layout is fine here.**

---

## Data model

**For:** how entities relate and what they hold.

- Show cardinality on every relationship. `1..*` and `0..*` are different facts and readers depend on the difference.
- List only the fields that matter to the point being made. A full column dump belongs in a table.
- Mark keys and required fields; leave types out unless the audience is engineers.
- **Accent:** the entity the discussion is about, or the relationship that is new or contested.

**Failure mode:** reproducing the schema. A data model diagram is an argument about structure, not documentation of every column.

**Auto-layout is fine here.**

---

## Timeline

**For:** what happened when, and in what order.

- One axis, consistently scaled — or explicitly not to scale, said in the caption. Silently uneven spacing is a lie about duration.
- Distinguish points (events) from spans (phases) visually.
- Label the axis with real units and state the as-of date.
- Collapse long empty stretches with an explicit break marker rather than compressing them silently.
- **Accent:** the event that caused the others, or the point the reader is being asked to notice.

**Failure mode:** a timeline where spacing implies duration but the data is ordinal. Say which one it is.

**Hand-author this one.** Spacing is the content.

---

## Swimlane

**For:** how responsibility is divided across actors.

- Lanes are actors or systems, never phases — phases run along the flow axis.
- Every handoff between lanes is the interesting part; label it.
- Keep lane order stable across related diagrams.
- If most of the work sits in one lane, a swimlane diagram is the wrong form.
- **Accent:** the handoff that fails, delays, or requires a decision.

**Failure mode:** more than five lanes. Group actors first.

---

## Quadrant

**For:** how options compare on two independent axes.

- Both axes need real, named criteria. If one axis is "goodness," this is not a quadrant.
- Verify the axes are actually independent. Correlated axes produce a diagonal smear and prove nothing.
- Label all four quadrants with what falling there means.
- Position is a claim. Be able to defend each placement, or state that placement is qualitative.
- **Accent:** the item under discussion, or the empty quadrant if the gap is the point.

**Failure mode:** the consultant 2×2 where everything lands in the top-right. If the placements are flattering to everything, the axes are not discriminating.

**Hand-author this one.** Position is the entire content.

---

## Layer stack

**For:** what sits on top of what.

- Only use it when the stacking relationship is real — "runs on," "abstracts over," "depends on." Boxes stacked because they are related is not a layer stack.
- Layers span the full width unless a layer genuinely covers only part of the one below, which is worth showing.
- Label what the boundary between layers is: an API, a protocol, a trust boundary.
- **Accent:** the layer being added, replaced, or discussed.

**Failure mode:** using it as a generic grouping device. Ask "does the top literally sit on the bottom?" If not, use a grouped architecture diagram.

**Hand-author this one.**

---

## Funnel

**For:** how something narrows or concentrates.

- Width must be proportional to the value, or the shape is misleading. If proportion is not available, use a bar chart.
- Label every stage with an absolute number and a conversion rate, and name the denominator for each rate.
- State whether stages are exclusive or cumulative.
- **Accent:** the stage with the largest drop.

**Failure mode:** a decorative funnel with equal-width stages. If the widths are not proportional it is a list drawn as a triangle. Consider whether this is really a chart — see `chart-design`.

---

## Venn

**For:** how sets overlap.

- Two or three sets. Four is not readable, whatever the tooling allows.
- Label the overlaps, not just the circles. The overlaps are the reason the diagram exists.
- If sizes are proportional, say so. If not, say that too.
- Do not use it to show a taxonomy — that is a tree.
- **Accent:** the intersection the argument depends on.

**Failure mode:** three circles where one overlap is empty. If a region has no members, the sets are not related the way the diagram claims.

---

## Tree / nested

**For:** how one thing decomposes into parts.

- Consistent decomposition rule at every level. Mixing "by function" at one level and "by team" at the next produces siblings that are not comparable.
- Depth over about four levels stops being readable; collapse or split.
- Nested containment reads as "part of"; edges read as "leads to." Do not mix the two idioms.
- Sibling order should mean something — size, sequence, priority — and the caption should say which.
- **Accent:** the branch under discussion.

**Failure mode:** an unbalanced tree presented as a taxonomy. If one branch has twelve children and the others have two, the decomposition rule is not doing its job.

---

## Change view

**For:** what a change adds, removes, and leaves alone — the before and after of one system, read together.

- Stack the two states on **shared columns**: today above, proposed below, every unchanged component directly above itself. The eye then reads only the difference; side-by-side states make the reader match boxes across a gap.
- Tag every changed node in words — `added`, `removed`, `changed` — above the node or its column. Never by colour or lightness alone: a theme swap or a grayscale print must not erase the change.
- Draw a removed component in the "today" state with a dashed outline and its tag; do not leave it out, or the reader cannot see what the new parts replace.
- Mute what does not change (`node-muted`). Present, legible, receding.
- Close with a **change ledger** inside the `viewBox`: one row per change, keyed by the node's real identifier (`dispatcher`, `ingest-a`), the change word, and one line on what it means. End with one line naming what is explicitly unchanged.
- **Accent:** the one added component the change hinges on, not every added box.

**Failure mode:** two complete architecture diagrams side by side with nothing marked. The reader plays spot-the-difference and misses the removal.

**Hand-author this one.** Column alignment is the content.

---

## Deployment map

**For:** where each part runs — cluster, namespace, workload, replicas — and what sits outside.

- Nest at most two levels of boundary: cluster, then namespace. A third level (node pool, zone) is a second diagram.
- Boundary labels carry the real identifiers in `var(--mono)` (`prod-ingest`, `ingest`) beside a short uppercase kind (`CLUSTER`, `NAMESPACE`).
- Show replicas as small pips inside their workload node, not as separate nodes: they are one deployment, and a row of full-size boxes reads as several services. Mark the scaling control the reader owns — the next replica as a dashed pip, the ceiling as text.
- Dependencies whose hosting the document does not establish sit outside every boundary, dashed, and the legend says the hosting is not shown. Placing a box inside a boundary is a claim about where it runs.
- A second environment that mirrors the first can be a slim boundary with one line of text, not a repeated drawing.
- **Accent:** the workload the reader will act on.

**Failure mode:** a cloud-console screenshot redrawn — every service, every zone, every load balancer. Keep only what the reader's task touches.

**Hand-author this one.** Containment is the content.

---

## Dependency graph

**For:** what must finish before what, and which chain sets the date.

- Directed and **acyclic**. A cycle is a planning error to resolve, not a shape to draw.
- Lay out left to right in date order: each column is a point in time, so position reads as "earlier" and "later". Put dates on the nodes in `var(--mono)`, and state the year once in the legend.
- Fan several incoming edges across the side they meet, at least 12px apart, so convergence on a gate reads as several distinct dependencies.
- Mark the **critical path as the one accent**: its edges in `var(--accent)` at 1.5px, its nodes outlined in accent. Every other edge stays muted. The legend says what the accent means ("a slip here moves production").
- A callout may name the risk on the critical path — the dependency with no confirmed owner — and nothing else.
- **Accent:** the critical path, and the single node on it the reader can still influence.

**Failure mode:** a Gantt chart turned sideways. If bars and durations matter more than precedence, use a timeline; this form is about what waits on what.

**Hand-author this one.** Auto-layout reorders columns by edge crossings and loses the date order.
