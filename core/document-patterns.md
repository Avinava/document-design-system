# Document patterns

Themes and patterns are independent axes.

- A **theme** sets visual voice through semantic tokens: paper, ink, accent,
  typography, borders, and status colour.
- A **pattern** sets reading behaviour through structure: where the answer
  appears, which relationships are visible, and which modules repeat.

The root element declares both:

```html
<html lang="en" data-theme="field-notes" data-pattern="decision">
```

Changing `data-theme` must not change the information architecture. Changing
`data-pattern` must not invent facts or alter the document's evidence state.
Pattern CSS lives in `core/document-patterns.css` and contains no colour
literals; every component consumes the active theme's semantic tokens.

## The eleven families

| Pattern | Reader movement | Characteristic modules | Types |
|---|---|---|---|
| `decision` | Orient to the ask, compare choices, record what is needed next | ask band, comparison grid, decision rail, non-goals | `design-doc`, `discovery`, `proposal`, `project-charter`, `estimate`, `change-request` |
| `record` | Confirm status, read the decision, trace consequences | decision statement, consequence grid | `adr` |
| `contract` | Find an exact rule, example, or compliance condition | contract index, requirement, specimen | `spec`, `api-contract`, `reference`, `requirements`, `statement-of-work`, `support-model` |
| `procedure` | Establish safety, execute in order, verify or recover | procedure steps, checkpoint, outcome, danger | `handoff`, `how-to`, `runbook` |
| `learning` | Build context, complete a path, consolidate understanding | learning goal, section number, reading time, checkpoint, section takeaway | `explanation`, `onboarding`, `tutorial` |
| `system` | Build a spatial model, then inspect boundaries and states | system map, system rail, state grid | `architecture`, `design-handoff` |
| `incident` | See severity first, reconstruct time, connect cause to action | impact strip, timeline, cause chain, action register | `postmortem` |
| `suite` | Orient across a linked documentation set | document map, table scroll | `service-docs` |
| `plan` | Follow work from baseline through dependencies and control gates | milestone rail, workstream board, plan gates | `delivery-plan`, `migration-plan`, `test-strategy` |
| `assurance` | See the verdict, inspect evidence, then accept or close exposure | assurance verdict, evidence matrix, finding register | `test-report`, `threat-model`, `readiness-review`, `risk-register` |
| `brief` | Read current state, material change, required action, next checkpoint | brief status, action required, brief grid, next checkpoint | `status-report`, `release-notes`, `workshop-summary`, `incident-update` |

The family is a constraint, not a page template. Two documents in the same
family may omit or reorder modules when their reader's question requires it.
The invariant is that they support the same reading movement. Each
characteristic module is named as it appears in the module registry below, and
at least one example of the pattern uses it.

## Openings

A pattern owns its opening: the first screen is built for the reader movement,
not shared by every document. Each opening is one or more hero parts placed
inside `.doc-hero`, and each pattern's section in `core/document-patterns.css`
gives `html[data-pattern="…"] .doc-hero` its grid. Every body of a pattern uses
its pattern's parts, and no two patterns share an opening or a part.

| Pattern | Opening | Hero parts |
|---|---|---|
| `decision` | Split hero with the facts a decider needs at the side | `hero-aside` |
| `record` | Status stamp plus record number | `hero-stamp` |
| `contract` | Index masthead | `hero-index` |
| `procedure` | Precondition checklist cover | `hero-checklist` |
| `learning` | Outcome first, with a generous measure | `hero-outcome` |
| `system` | The map in the hero | `hero-figure` |
| `incident` | Full-width severity band with impact numbers | `hero-band` |
| `suite` | Service index | `hero-services` |
| `plan` | Milestone-rail masthead | `hero-rail` |
| `assurance` | Verdict stamp | `hero-verdict` |
| `brief` | Dated compact masthead on a one-screen grid | `hero-dateline` |

A pattern also sets its own pace in the same section of the stylesheet:
`--pattern-density` (multiplies the theme's `--density`), `--doc-max`, the
section gap and rule weight, the reading measure, and the section-number style.
Hero parts are shell classes, listed here and in `scripts/catalog.py`; they
are not modules and are not used outside `.doc-hero`.

## Selection

Use a type when one fits; compose from a pattern when none does.

1. **A type or alias fits.** Its reference file declares the default pattern
   and theme. Override the theme freely when the audience needs a different
   voice. Overriding a type's pattern still means the type is wrong: pick the
   type whose reader movement matches, or compose.
2. **No type fits.** Pick the pattern whose reader movement answers the
   reader's question, then compose the page from modules that pattern allows
   in the registry, borrowing section discipline from the nearest type. The
   theme is the nearest type's default. A composed document declares
   `type: custom` with its `pattern`, `modules`, and `nearest-type`.

A composed shape seen three times becomes a type. That is the only way the
catalog grows.

Do not collapse every page back to a centred stack of headings and cards.
Prose remains readable at 62–72 characters, while tables, maps, timelines,
comparisons, and action registers may use the wider document shell.

A reader who asks for a full-width page gets `<html data-width="full">` (build
flag `--width full`). The shell then fills the viewport on wide screens while
prose keeps its measure. Width is not a pattern and not a theme, and no pattern
or module may depend on it.

## Modules

A module is a class in `core/document-patterns.css` that carries one reading
job. This registry is the complete list: every module class in the stylesheet
appears here, and every class here exists in the stylesheet. A body — type
preset or composed — uses only modules its pattern allows. `any` means the
module serves every pattern.

| module | class | patterns allowed | purpose |
|---|---|---|---|
| key point | `keypoint` | any | One sentence the reader should carry out of the section |
| evidence note | `evidence` | any | Source and evidence state for the claim just made |
| figure | `figure` | any | Captioned diagram or chart |
| table scroll | `table-scroll` | any | Wide table that scrolls inside itself on narrow screens |
| footnotes | `footnotes` | any | Sources and asides kept out of the reading line |
| section number | `section-num` | any | Numbered section marker inside a section head |
| reading time | `reading-time` | any | Time or role label at the end of a section head |
| table of contents | `toc` | `learning`, `contract`, `suite` | Ordered path through a long document |
| non-goals | `non-goals` | `decision`, `contract`, `plan` | What this document deliberately does not decide or cover |
| checkpoint | `checkpoint` | `learning`, `procedure` | Observable state that proves the reader may continue |
| section takeaway | `takeaway` | `learning`, `procedure`, `incident`, `system`, `suite` | The per-section conclusion, stated after the material that earns it |
| danger | `danger` | `procedure`, `contract`, `plan`, `assurance` | Irreversible or unsafe action, before the step that risks it |
| specimen | `specimen` | `contract`, `learning`, `procedure`, `system` | Exact request, payload, or command with a caption |
| comparison grid | `comparison-grid` | `decision`, `record`, `learning`, `incident` | Options or distinctions judged on the same criteria |
| ask band | `ask-band` | `decision` | The decision asked for, by whom, by when, and the default if declined |
| decision grid | `doc-grid` | `decision` | Argument column beside the decision rail |
| decision rail | `decision-rail` | `decision` | Sticky brief: the ask, guardrails, open questions |
| scope strip | `scope-strip` | `learning`, `decision`, `brief`, `system` | Who it is for, read time, companion documents, and what it is not |
| crosswalk | `crosswalk` | `learning`, `decision`, `contract`, `system` | Term in the reader's world mapped to the term here, with fit and note |
| learning goal | `learning-goal` | `learning` | What the reader will be able to do or explain at the end |
| decision statement | `decision-statement` | `record` | The settled choice in one block |
| consequence grid | `consequence-grid` | `record` | What the choice makes easier and harder |
| contract layout | `contract-layout` | `contract` | Index column beside the normative text |
| contract index | `contract-index` | `contract` | Sticky list of rules or sections |
| requirement | `requirement` | `contract`, `assurance` | Identified rule with its condition |
| endpoint | `endpoint` | `contract` | Method and path with its behaviour |
| procedure steps | `procedure-steps` | `procedure`, `learning` | Numbered steps on a rail |
| outcome | `outcome` | `procedure`, `learning` | Observable success after a step |
| response band | `response-band` | `procedure` | Parallel responses side by side: verify, roll back, escalate |
| system map | `system-map` | `system`, `decision`, `learning` | Framed architecture figure |
| system layout | `system-layout` | `system` | Map column beside the boundary rail |
| system rail | `system-rail` | `system` | Boundaries, owners, and interfaces beside the map |
| state grid | `state-grid` | `system` | One card per state the reader must handle |
| impact strip | `impact-strip` | `incident`, `decision`, `assurance` | Three headline measures before any narrative |
| timeline | `timeline` | `incident` | Timestamped reconstruction |
| cause chain | `cause-chain` | `incident`, `learning`, `system` | Cause to effect in reading order |
| action register | `action-register` | `incident` | Owned corrective actions |
| document map | `document-map` | `suite`, `procedure` | Cards linking the documents in a set |
| plan layout | `plan-layout` | `plan` | Plan column beside the gate rail |
| plan gates | `plan-gates` | `plan` | Control gates and their criteria |
| milestone rail | `milestone-rail` | `plan` | Dated milestones in order |
| workstream board | `workstream-board` | `plan` | One card per workstream |
| assurance layout | `assurance-layout` | `assurance` | Verdict column beside the evidence |
| assurance verdict | `assurance-verdict` | `assurance` | The verdict and its conditions |
| verdict | `verdict` | `assurance` | Inline verdict for one finding or test set |
| finding register | `finding-register` | `assurance` | Findings with severity and owner |
| evidence matrix | `evidence-matrix` | `assurance` | Claims against the evidence that supports them |
| brief status | `brief-status` | `brief` | Current state in three cells |
| brief grid | `brief-grid` | `brief` | Update cards for what changed and what needs attention |
| next checkpoint | `next-checkpoint` | `brief` | When and where the next update lands |
| action required | `action-required` | `brief` | The one action a reader must take |
| range bar | `range-bar` | `decision` | An estimate's expected value inside its range, with confidence |
| delta ledger | `delta-ledger` | `decision` | What a change request alters against the baseline: added, moved, held, pending |
| rollout strip | `rollout-strip` | `decision` | Rollout phases in order, each a stop on one bar |
| go-stop criteria | `go-stop` | `decision` | The tests that send a discovery to go, reframe, or stop |
| roster | `roster` | `decision` | Who holds which part of an agreement |
| cost ledger | `cost-ledger` | `decision` | What the ask costs, what it displaces, and what it leaves running |
| conformance | `conformance` | `contract` | Each requirement's keyword level, proof, and gate |
| error catalog | `error-catalog` | `contract` | Stable error codes with retry and the caller's action |
| config keys | `config-keys` | `contract` | Configuration keys with required or optional, meaning, and default |
| unchanged list | `unchanged-list` | `contract` | The surfaces a requirement set leaves untouched |
| deliverable ledger | `deliverable-ledger` | `contract` | Deliverables by acceptance gate date and owner |
| priority ladder | `priority-ladder` | `contract` | Priorities from most to least urgent with the first owner |
| check list | `check-list` | `procedure` | Items to tick off, each a box |
| result check | `result-check` | `procedure` | The observable result that proves the task is done |
| term list | `term-list` | `learning` | The words an explanation leans on, defined once |
| lesson path | `lesson-path` | `learning` | The whole lesson as stops on a trail, each with its time |
| component spec | `component-spec` | `system` | Each component with what it is for and what stays out |
| freshness | `freshness` | `suite` | How each kind of document in a set keeps its evidence current |
| dependency flags | `dependency-flags` | `plan` | The dependencies that can move a gate |
| preflight | `preflight` | `plan` | Preconditions that must hold before a gate opens |
| layer stack | `layer-stack` | `plan` | Layers of test evidence, each with what it proves and who owns it |
| RAG strip | `rag-strip` | `brief` | The red, amber, green scale with the current state marked |
| change ledger | `change-ledger` | `brief` | Each change under the word that classifies it |
| agreements | `agreements` | `brief` | What a meeting settled and what it left open |
| update clock | `update-clock` | `brief` | Start, this update, and the next update on one line |
| exposure board | `exposure-board` | `assurance` | Register items grouped by exposure rating |
| threat matrix | `threat-matrix` | `assurance` | Each threat, its control, and the residual state |

The section takeaway is the `takeaway` class used at the end of a section; it
is not a second class. Shell classes (`doc`, `doc-hero`, `lede`, `doc-meta`,
`status-banner`, `section`, `section-head`, `component-label`, `lang`) frame
every page and are not modules. Parts live inside one module and are not used
alone: `recommended` (comparison grid), `requirement-id` (requirement),
`http-method` (endpoint), `impact-value` and `impact-label` (impact strip),
`crosswalk-legend` (crosswalk). A crosswalk marks fit on its cell with
`data-fit="holds|partial|breaks"` and always writes the word. The ledger and
strip modules mark status with `<b data-tone="positive|warning|critical|accent">`
and write the word there too; the attribute is not a class and not a part.
Every type's body carries at least one module no other type uses, so documents
of one pattern differ below the hero as well as in it.
`scripts/catalog.py` declares the same shell and part lists for the checks.

Allowed patterns record intended reuse, not only the pattern a module was
first drawn for. A learning page may borrow a cause chain from the incident
family because explaining a failure is a learning job; it may not borrow a
plan's gate rail, because that would change how the page is read.

## Fonts and portability

Web previews and GitHub Pages link to the declared Google Fonts so the intended
voice is visible without inflating every HTML file. Offline, email, archival,
and PDF deliverables must embed or package fonts explicitly, or use a verified
system-font fallback. A linked font is not an offline promise.

## Acceptance checks

- The root has a known `data-pattern` and `data-theme`.
- The type reference, generated HTML, and gallery agree on both defaults.
- The pattern exposes its characteristic modules before decoration is judged.
- At 390px, reading order is unchanged and no page-level horizontal scroll is
  introduced. Wide tables may scroll inside `.table-scroll`.
- In print, grids and tables remain intentional, headings do not strand, and
  code does not clip.
- `core/document-patterns.css` contains no colour literals.
