# Document types

Section-by-section guidance. Each type has a shape readers already know; matching it means their attention goes to the content rather than to the document.

## Contents

- [Design doc / RFC](#design-doc--rfc)
- [Architecture decision record](#architecture-decision-record)
- [Specification](#specification)
- [Postmortem](#postmortem)
- [Proposal](#proposal)
- [Runbook](#runbook)

---

## Design doc / RFC

**Reader's question:** should we do this, and is the approach sound?

| Section | Content |
|---|---|
| Summary | Three sentences. What, why, what changes. Written last |
| Context | What a reader needs to hold in mind. Not a history lesson |
| Problem | What is wrong now, with evidence. Numbers where they exist |
| Goals | What success looks like, ideally measurable |
| Non-goals | What this explicitly does not address |
| Proposal | The design. The bulk of the document |
| Alternatives considered | Real options, with real reasons for rejection |
| Risks and mitigations | What could go wrong and what happens if it does |
| Rollout | How it ships, how it is verified, how it rolls back |
| Open questions | With owners and dates |

**Notes:**

- Write the summary last. A summary written first describes the document you intended.
- The problem section needs evidence. "The current system is hard to maintain" is an opinion; "four of the last six incidents traced to the same coupling" is a problem.
- Non-goals prevent the review sprawling into adjacent problems, and surface mental-model mismatches early.

**Failure mode:** a proposal section that describes the implementation without ever stating the design. If a reader cannot restate the approach in a sentence after reading it, the section is describing code rather than a design.

---

## Architecture decision record

**Reader's question:** why is it like this?

| Section | Content |
|---|---|
| Title | The decision, as a statement: "Use Postgres for the event store" |
| Status | Proposed / Accepted / Superseded by <link> / Deprecated |
| Context | The forces at play — technical, organizational, temporal |
| Decision | What was decided, in the active voice |
| Consequences | What follows, both good and bad |

**Notes:**

- **One decision per record.** A record with three decisions cannot be superseded cleanly.
- **Immutable once accepted.** To change a decision, write a new ADR that supersedes it. The old record keeps its content and gains a pointer. Editing it destroys the record of why the original decision made sense.
- Context should include what was true *at the time*. A decision that looks wrong later often made sense given constraints that have since gone away, and the record should let a future reader see that.
- Consequences must include the bad ones. An ADR listing only benefits is marketing.

**Failure mode:** ADRs written after the fact to justify a decision already made. They read as reasonable and teach nothing, because the real forces are absent.

---

## Specification

**Reader's question:** what exactly must I build, and how do I know I am done?

| Section | Content |
|---|---|
| Scope | What this specifies, and what it does not |
| Definitions | Terms with precise meanings, referenced throughout |
| Requirements | Normative statements, individually identified |
| Examples | Concrete cases, including edge cases |
| Compliance | How conformance is determined |

**Notes:**

- Use RFC 2119 keywords (MUST, SHOULD, MAY) and say at the top that you are doing so. Without that, "should" is ambiguous between a requirement and a suggestion.
- **Give every requirement a stable identifier** (`REQ-014`). Tests, reviews, and bug reports all need something to reference, and section numbers shift.
- Examples are normative in practice, whatever the document says — implementers read them first and copy them.
- Specify error and boundary behavior. Unspecified means every implementation differs.

**Failure mode:** mixing normative requirements with explanatory prose so an implementer cannot tell which sentences bind. Separate them visually.

---

## Postmortem

**Reader's question:** what happened, why, and what stops it recurring?

| Section | Content |
|---|---|
| Summary | What broke, for how long, affecting whom |
| Impact | Quantified — users, requests, revenue, duration |
| Timeline | Detection through resolution, with timestamps and timezone |
| Root cause | The technical chain, followed to the end |
| Contributing factors | What made it worse, slower to detect, or harder to fix |
| What went well | Genuinely — this is how good practice gets reinforced |
| Action items | Owner, priority, tracking link, each |

**Notes:**

- **Blameless.** Name systems and processes, not people. "The deploy did not have a staging gate," not "X deployed without testing." People who expect blame write less honest timelines, and the timeline is the most valuable part.
- **Timestamps with a timezone.** A timeline in unlabelled local time is unusable.
- Include detection time separately from resolution time. Slow detection is usually the more actionable problem.
- Action items without owners do not happen. Action items without tracking links are not tracked.

**Failure mode:** stopping at the first plausible cause. "The disk filled up" is not a root cause — why was there no alert, why did it fill, why did the service fail hard rather than degrade?

---

## Proposal

**Reader's question:** should I approve this?

| Section | Content |
|---|---|
| The ask | What you want, stated first, in one sentence |
| Rationale | Why it is worth it |
| Cost | Time, money, people, opportunity cost |
| Alternatives | Including doing nothing |
| Decision needed | Who decides, by when, and what happens if they do not |

**Notes:**

- The ask goes first. A proposal that builds to its request wastes the reader's most attentive minute.
- Include doing nothing as an alternative, with its cost. It is always an option and is often chosen by default.
- State the cost honestly, including the parts that are hard to quantify. A proposal that understates cost damages the next one you write.

**Failure mode:** an ask so vague it cannot be approved. "Investment in platform reliability" is not decidable; "two engineers for one quarter to add staging gates to the deploy pipeline" is.

---

## Runbook

**Reader's question:** what do I do right now?

| Section | Content |
|---|---|
| When to use | The symptom or trigger |
| Preconditions | Access, tools, state required before starting |
| Steps | Numbered, imperative, individually verifiable |
| Verification | How to confirm it worked |
| Rollback | How to undo it |
| Escalation | Who to contact, and when to stop trying |

**Notes:**

- Written for someone tired, at 3am, who did not write the system. Assume no context.
- Every step is one action, and says how to tell it succeeded.
- Include the actual commands, copy-pasteable, with placeholders clearly marked.
- Say what to do when a step fails — that is when the runbook is actually being read.
- **Date the runbook and name its owner.** Stale runbooks are worse than none, because they are followed.

**Failure mode:** prose. A runbook is a checklist. Anything explanatory goes in a linked design doc, not inline where it slows down someone in an incident.
