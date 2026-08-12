# Evidence semantics

The distinctions in this file are where analytical documents actually fail. The design can be flawless and the document still wrong, because a column was labelled `Owner` when it held the last modifier, or because current size grouped by creation date was captioned as growth.

## Contents

- [The evidence model](#the-evidence-model)
- [Control totals](#control-totals)
- [Analytical views](#analytical-views)
- [Time and change semantics](#time-and-change-semantics)
- [Classification](#classification)
- [Facts, interpretations, recommendations](#facts-interpretations-recommendations)

## The evidence model

Before designing, identify:

- The unit being measured.
- The population included and excluded.
- Which values are counts, quantities, percentages, limits, or estimates.
- Which fields are direct facts and which are inferred classifications.
- Whether dates mean creation, occurrence, update, ingestion, or observation.
- Whether people fields identify authors, owners, operators, approvers, or deployment accounts.
- Whether the dataset is a current snapshot or a historical series.

Write these into the report. A reader who has to guess will guess wrong, and will be confident about it.

## Control totals

Calculate the document's control totals before deriving any chart.

- Included groups must sum to the reported total.
- Excluded populations must be shown separately, not silently dropped.
- Percentages must use a named denominator, stated near the figure.
- Rounded labels must not conceal material discrepancies.
- If an external control total exists, state whether the report reconciles to it.

Stop and investigate unexplained differences. Styling inconsistent data into apparent authority is worse than shipping nothing — it converts a data problem into a decision problem.

## Analytical views

Prefer views that answer distinct questions. If two views answer the same question, one of them is decoration.

| View | Question answered |
|---|---|
| Current-state ledger | How much is used, available, included, or excluded? |
| Functional concentration | Which capabilities or categories hold most of the quantity? |
| Ownership concentration | Who appears responsible for most of the current footprint? |
| Creation cohorts | Which vintages make up today's population? |
| Recent activity | What was created or modified recently? |
| Staleness | What has not changed within a meaningful period? |
| Version posture | How much remains on older standards or compatibility levels? |
| Largest units | Which individual records dominate the total? |
| Review candidates | Which records meet a transparent triage rule? |

Do not add a chart merely because a field exists.

## Time and change semantics

Time-based reporting is the most frequently overstated part of an analytical document.

### Snapshot cohorts are not historical growth

If each record has a creation date and a current size, grouping current size by creation date means:

> Current footprint of records created during each period.

It does **not** mean:

> Amount added during each period.

Records may have grown, shrunk, or been replaced after creation. Use wording such as "current size by creation cohort" unless historical snapshots or change events actually exist.

This single mislabel is the most common serious error in inventory reporting, and it is invisible to the reader — the chart looks identical either way.

### Show both years and recent months

- Years for long-term composition.
- Collapse old years into a clearly labelled legacy cohort when density is too high.
- Trailing 12 months for recent monthly detail.
- Keep missing months visible as zero when showing a continuous trend, so gaps read as gaps rather than as absence of data.
- State the report's as-of date.

### Creation and modification answer different questions

- Creation date indicates when the record entered the observed system.
- Modification date indicates the latest recorded change, not necessarily substantive development.
- Modifier identity may represent an automation or deployment account, not a person.
- Staleness indicates inactivity, not irrelevance.

### Historical growth requires history

For true growth reporting, at least one of these must exist:

- Periodic snapshots using the same measurement method.
- Source-control history with reliable file metrics.
- An append-only event or audit log.
- Versioned exports with stable identifiers.

If none exists, say so in the methodology rather than approximating growth from a snapshot.

## Classification

Classification is often necessary and often inferred. The document should be honest about which.

### Rule order

Apply the most specific rules first:

1. Explicit known prefixes, product names, or authoritative mappings.
2. Exact record-name patterns.
3. Name keywords.
4. Source or description keywords.
5. `Other / Needs Review`.

A specific family must not be fragmented because its records also contain generic terms. Ordering the rules this way is what prevents that.

### Confidence

Store classification confidence with each record:

- `High` — authoritative mapping or explicit name/prefix.
- `Medium` — strong content or metadata evidence.
- `Low` — weak keyword inference or fallback.

Show a count of low-confidence records in the document, and preserve the per-record classification in the detailed export so a reader can audit it.

### Category quality

Good categories are mutually understandable, useful to a decision-maker, and stable across report runs.

Avoid categories that mix business functions, technical patterns, and teams in one dimension. Keep these as separate dimensions:

- Business function
- Technical role
- Ownership or stewardship
- Age or lifecycle
- Version or standard

Mixing them produces a chart where no bar is comparable to any other bar, which is worse than having no chart.

## Facts, interpretations, recommendations

Use explicit language and keep the three separate:

- **Fact:** "42 records total 1.8 million units."
- **Interpretation:** "This concentration may increase dependency risk."
- **Recommendation:** "Review ownership and replacement options."

Avoid converting weak signals into conclusions:

- A large file is not automatically poor quality.
- An old version is not automatically broken.
- A test-like name does not prove a record is disposable.
- A single owner on many records may reflect a deployment account, not a person.

Review candidates are candidates. Presenting them as guaranteed savings is the point at which an analytical document stops being evidence and becomes advocacy.
