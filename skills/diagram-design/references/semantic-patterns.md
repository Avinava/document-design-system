# Semantic patterns

What each visual device means in this system, so a reader and a checker can rely on the same reading. Use it before choosing a form: decide which relationship the reader needs, find its device here, then open `diagram-families.md` for the form that draws it.

## Contents

- [Devices and what they claim](#devices-and-what-they-claim)
- [Relationship to form](#relationship-to-form)
- [Reading direction](#reading-direction)
- [Claims a diagram must not make by accident](#claims-a-diagram-must-not-make-by-accident)

## Devices and what they claim

| Device | Claims | Use it for | Never for |
|---|---|---|---|
| Containment (a boundary around nodes) | Part of; runs inside; owned by | Trust zones, clusters, releases | Grouping that is only visual tidiness |
| Adjacency (nodes close together) | Coupled or related | Position-carrying forms such as architecture | Spacing chosen for symmetry |
| Solid edge with arrowhead | Direct, synchronous, primary flow | The main path | A relationship with no direction |
| Dashed edge | Asynchronous, optional, inferred, or automated | Queues, fallbacks, automations | Decoration |
| Dotted edge | A reference or weak relationship | Links between figures and notes | Anything the reader must follow |
| Position on an axis | A placement the author can defend | Quadrant, evolution map, timeline | Layout convenience |
| Width or length | A quantity | Funnel, pyramid, bars | Emphasis |
| Dashed outline on a node | Outside the boundary, removed, or not yet built | External systems, removed components | Muted context (use `node-muted`) |
| Accent | Look here first | The one or two things the argument rests on | A category |
| A word on the figure | What a change, state or lane is | Tags such as `added`, lane labels, stage names | Nothing: words are the fallback for every other device |

The last row is the rule underneath the rest: any meaning carried by line style, fill or position must also be stated in words somewhere on the figure, so it survives grayscale and a theme change.

## Relationship to form

| The reader's question has this shape | Relationship | Form |
|---|---|---|
| What is part of what, and what runs where | Containment | Architecture, deployment map, tree |
| What follows what | Sequence | Flow, sequence, timeline, journey |
| What waits on what | Precedence | Dependency graph |
| What causes what | Causation | Fishbone, cycle |
| What changed | Difference | Change view |
| How big is each | Quantity | Funnel, pyramid, chart |
| How do options compare | Two independent axes | Quadrant, evolution map |
| Who does what | Responsibility | Swimlane, event model |
| What is recorded and what reads it | Record and read | Event model |
| What is the thinnest path | Ordered scope | Story map |

If a question has two rows, it is two diagrams. If it matches no row, it probably wants a table.

## Reading direction

| Subject | Direction | Why |
|---|---|---|
| Process, time, stages | Left to right | The eye already reads that way |
| Hierarchy, layers, dependence on a base | Top to bottom | Higher means more visible or more abstract |
| Cause to effect | Toward a labelled end point | Fishbone leans toward the effect |
| A closed loop | Clockwise from the top | Cycles have no start; the top gives one |

Do not mix two directions in one figure. A flow whose columns are time and whose rows are also an ordering has two axes and needs both labelled.

## Claims a diagram must not make by accident

- **Order that is not ordinal.** Left-to-right implies "earlier"; if the items are unordered, say so in the caption.
- **Size that is decoration.** If width or area varies, it will be read as quantity.
- **A closed shape that is not a loop.** Joining the last step to the first claims it feeds the first.
- **Symmetry as balance.** Equal columns imply equal weight; if one column carries most of the load, size or annotate it.
- **Proximity as relation.** Two nodes near each other read as related even with no edge. Keep unrelated nodes a full node gap apart.
- **Colour as category.** Categories take labels or shape, never fill.
