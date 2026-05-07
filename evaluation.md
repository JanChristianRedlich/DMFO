# B2-CCO Baseline Implementation — Claude Code Instructions

## Context

This task implements **B2-CCO**, an alternative-architecture baseline for the DMFO ontology paper. DMFO is a modular OWL 2 DL alignment framework that connects six dimensional vocabularies (PROV-O, SOSA/SSN, DUL/DnS, GeoSPARQL, OWL-Time) via six typed bridge axioms (A1–A6). B2-CCO is a non-tautological comparison baseline: instead of a strawman ablation, it implements the same competence-question coverage problem on top of the **Common Core Ontologies (CCO)**, a BFO-based mid-level ontology suite that uses fundamentally different modelling idioms.

The point of B2-CCO is **not** to win or lose against DMFO. It is to demonstrate, via a faithful CCO-native implementation, *which* anchor competence questions become structurally hard to answer when the architecture follows BFO's continuant/occurrent split and CCO's quality-inherence + ICE-based modelling instead of DMFO's typed-bridge architecture.

**Read this entire file before writing any code or asking clarifying questions.** Then read `docs/b2-cco-mapping.md` (will be created in step 1) before each subsequent step.

## Hard rules — do not violate

1. **Do not replicate DMFO's typed bridges in CCO clothing.** No property called `b2cco:evidencedBy` or `b2cco:stateWasGeneratedBy`. If a slot has no native CCO pendant, fall back to standard CCO modelling patterns documented in the FOIS 2024 paper (Jensen et al.) or the official "Modeling with CCO" guides. Each modelling decision must cite a source.
2. **Use CCO 2.0 opaque IRIs in all ontology files.** CCO since v2.0 uses `https://www.commoncoreontologies.org/ont00000xxx`-style identifiers, not human-readable names. The mapping file (CSV from CCO GitHub) lives at `validation/b2-cco/vendor/cco-2.0-mapping.csv` after step 1. Use `rdfs:label` to make snippets readable for humans, but never invent custom readable IRIs for CCO terms.
3. **Two domain instantiations: Maritime (mandatory) and Food (optional).** Implement Maritime first end-to-end. Only start Food after Maritime is complete and reviewed. If time pressure: report Food as future work in the manuscript.
4. **Every modelling decision goes into an ADR** (Architecture Decision Record) in `validation/b2-cco/docs/adr/`. No undocumented choices. ADR template is in step 2.
5. **Never edit DMFO files.** B2-CCO lives entirely in `validation/b2-cco/`. The DMFO ontology and ABox files at the repo root are read-only references.
6. **No hidden tuning.** If a CCO modelling pattern fails on an ACQ, document the failure in `docs/acq-translation.md` with diagnosis. Do not "fix" the modelling to make the ACQ pass unless the fix is itself a documented standard CCO pattern.

## Repository structure to create

```
validation/b2-cco/
├── README.md
├── vendor/
│   ├── cco-2.0/                 # cloned CCO repo, read-only
│   └── cco-2.0-mapping.csv      # CCO label→IRI mapping
├── docs/
│   ├── slot-mapping.md          # DMFO slot → CCO pattern table
│   ├── faithful-translation-rule.md
│   ├── acq-translation.md       # ACQ-by-ACQ DMFO→CCO translation log
│   └── adr/
│       ├── 000-template.md
│       ├── 001-state-as-quality.md
│       ├── 002-activity-as-cco-act.md
│       ├── 003-evidence-fallback.md
│       ├── 004-context-as-action-regulation.md
│       └── 005-location-with-or-without-geosparql.md
├── ontology/
│   ├── b2-cco-base.ttl          # CCO imports + minimal additions
│   ├── b2-cco-maritime.ttl      # Maritime profile
│   └── b2-cco-food.ttl          # Food profile (later)
├── abox/
│   ├── maritime-abox.ttl
│   └── food-abox.ttl
├── queries/
│   ├── acq-01-cco.rq
│   ├── …
│   └── acq-20-cco.rq
├── results/
│   ├── b2-cco-results.json
│   └── b2-cco-perf.json
├── tests/
│   ├── consistency-check.sh     # HermiT classification
│   ├── oops-check.sh            # OOPS! pitfall scan
│   └── run-acqs.sh              # SPARQL execution
└── Dockerfile                   # reproducible eval environment
```

## Step-by-step task breakdown

Work through these steps **in order**. After each step, stop and produce a short status report (what was done, what is left, what blocks). Do not auto-proceed to the next step without my confirmation, *except* where explicitly marked "auto-proceed".

### Step 1 — Setup (auto-proceed)

1. Create the directory structure above.
2. Clone CCO 2.0 into `validation/b2-cco/vendor/cco-2.0/`:
   ```
   git clone --depth 1 https://github.com/CommonCoreOntology/CommonCoreOntologies.git validation/b2-cco/vendor/cco-2.0
   ```
3. Locate the CCO 2.0 IRI-to-label mapping file in the cloned repo (it is referenced in the README — search for "mapping file"). Copy or symlink it as `validation/b2-cco/vendor/cco-2.0-mapping.csv`.
4. Create a top-level `validation/b2-cco/README.md` with: purpose statement, link to this CLAUDE.md, link to the DMFO main repo README, build/test commands.
5. Create `docs/faithful-translation-rule.md` with the rule text from the manuscript draft (I will paste it; if not yet pasted when you reach this step, halt and ask).
6. Verify HermiT is available (Java reasoner). If not, document install steps in `tests/README.md`.

**Status report after step 1:** confirm directory created, CCO version cloned (which commit hash), mapping file present, HermiT available.

### Step 2 — Slot mapping document (stop and review)

1. Create `docs/adr/000-template.md` with this ADR template:
   ```markdown
   # ADR-NNN: <decision title>

   **Status:** proposed | accepted | superseded
   **Date:** YYYY-MM-DD
   **DMFO slot affected:** <Identity | State | Activity | Evidence | Context | Location>

   ## Context
   What is the modelling problem? What does DMFO do here, and why does that not directly transfer to CCO?

   ## Options considered
   - Option A: …
   - Option B: …
   - Option C: …

   ## Decision
   Selected option, with one paragraph rationale.

   ## CCO source
   - Citation to FOIS 2024 paper (Jensen et al., section X.Y) OR
   - Citation to official "Modeling with CCO" guide (page X) OR
   - Citation to a CCO-conformant published example
   - Verbatim CCO IRIs used (opaque + label).

   ## Consequence
   Which ACQ classes does this enable? Which does it block, and why?

   ## SPARQL/Turtle illustration
   Minimal example (5–10 lines).
   ```

2. Create `docs/slot-mapping.md` with this exact table structure (filled rows are placeholders for me to confirm):

   | DMFO slot | DMFO anchor | CCO pendant (label) | CCO IRI | Source | ADR | Notes |
   |---|---|---|---|---|---|---|
   | Identity | `cspo:TimeVaryingEntity` | `cco:Object` (or `bfo:material entity`) | TBD | FOIS24 §X | ADR-001 | … |
   | State | `cspo:Manifestation` | quality-inherence pattern | TBD | FOIS24 §3 | ADR-001 | NO direct class equivalent |
   | Activity | `prov:Activity` | `cco:Act` (intentional) / `bfo:process` | TBD | FOIS24 §4 | ADR-002 | |
   | Agent | `prov:Agent` | `cco:Agent` | TBD | FOIS24 §4 | ADR-002 | material entities only |
   | Evidence | `sosa:Observation` | NONE — fallback needed | — | — | ADR-003 | two variants (a) co-import SOSA (b) CCO-native measurement pattern |
   | Context | `dul:Situation`/`dul:Description` | `cco:Action Regulation` (subclass of `cco:Directive ICE`) | TBD | FOIS24 §5 | ADR-004 | normative content only, NO multi-regime situation |
   | Location | `geo:Feature` | `cco:Geospatial Region` / `cco:Site` | TBD | FOIS24 §6 | ADR-005 | no native topology reasoning |

3. **Stop here.** Produce the table with TBD-placeholders filled in based on actual CCO 2.0 IRIs from the mapping file. Do not draft the ADRs yet — I will review the mapping table first and may correct it.

**Status report after step 2:** mapping table populated, IRIs verified against CCO 2.0 mapping CSV, list of open questions.

### Step 3 — Author ADRs (stop and review after each ADR)

For each of ADR-001 through ADR-005, draft the ADR following the template, **one at a time**, and pause for review after each. Do not auto-proceed.

Order: 001 → 002 → 003 → 004 → 005. ADR-003 (Evidence fallback) is the most consequential — produce both variant (a) and variant (b) as separate sub-ADRs (003a, 003b). Both will be implemented and evaluated, because the comparison between them is itself a finding.

**For each ADR, the SPARQL/Turtle illustration must be runnable.** Test it in `validation/b2-cco/tmp/adr-NNN-test.ttl` against an empty CCO import to verify syntactic correctness.

### Step 4 — Base ontology and Maritime profile (stop and review)

1. `ontology/b2-cco-base.ttl`:
   - Imports CCO 2.0 (Agent, Event, Information Entity, Geospatial, Time, Quality, Artifact, Facility — exact list per ADRs).
   - Adds *only* the minimal CCO-conformant additions justified in ADR-003 (evidence fallback) and ADR-005 (location bridge if applicable).
   - No other axioms. No DMFO bridges. No typed inter-dimensional properties beyond what the ADRs justify.

2. `ontology/b2-cco-maritime.ttl`:
   - Imports `b2-cco-base.ttl`.
   - Defines maritime-specific subclasses of CCO classes (e.g. `mar:Container` ⊑ `cco:Object`, `mar:Yard` ⊑ `cco:Site`).
   - One-to-one correspondence with the maritime classes used in DMFO's maritime profile: same number of classes, same domain coverage, but typed under CCO instead of `cspo:` anchors.

3. Run `validation/scripts/b2cco-consistency-check.sh` (which runs HermiT). Profile must classify without unsatisfiable classes.

**Status report after step 4:** consistency confirmed, class count matched against DMFO maritime profile, any deviations noted.

### Step 5 — Maritime ABox re-implementation (stop and review)

1. Read `<repo-root>/abox/maritime-abox.ttl` (DMFO maritime ABox) carefully.
2. For each individual in DMFO maritime ABox, create the CCO-conformant counterpart in `validation/b2-cco/abox/maritime-abox.ttl`. **Same individuals, same scenario, different modelling.**
3. For each major modelling shift (especially: state phases → quality-inherence + process profile), produce a side-by-side diff in `docs/abox-translation-maritime.md` showing DMFO triple block ↔ B2-CCO triple block.
4. Maintain a running tally: number of DMFO triples, number of B2-CCO triples, ratio. Significant divergence (e.g. CCO needs 1.5× more triples for the same scenario) is itself a finding — note it in the doc.

**Status report after step 5:** ABox triple counts (DMFO vs. B2-CCO), translation diff doc completed, HermiT consistency on TBox+ABox confirmed.

### Step 6 — ACQ translation and SPARQL queries (stop after first 5 ACQs, then auto-proceed)

1. Read DMFO's 20 ACQs from `<repo-root>/queries/`.
2. For each ACQ, in `docs/acq-translation.md`:
   - Quote the original DMFO SPARQL.
   - Classify: (a) directly translatable, (b) translatable with modelling rework, (c) translatable but unanswerable in CCO, (d) not meaningfully translatable.
   - For (a)–(c), write the CCO-SPARQL counterpart in `queries/acq-NN-cco.rq`.
   - For (c)–(d), write a one-paragraph diagnosis: which CCO modelling commitment blocks the answer? Cite the relevant ADR.
3. **Pause after ACQ 1–5** for my review. After review, auto-proceed through ACQ 6–20 using the same approach.

**Status report after first 5 ACQs:** classification table, queries drafted, diagnoses for any (c)/(d) cases.

### Step 7 — Run evaluation (auto-proceed)

1. `validation/scripts/b2cco-run-acqs.sh`: executes all 20 CCO-SPARQL queries against the maritime ABox via Apache Jena, captures result counts and execution times.
2. Output `results/b2-cco-results.json` with per-ACQ: status (✓ / ◑ / ✗), result count, classification, diagnosis-ADR-link.
3. Output `results/b2-cco-perf.json` with median over 5 runs of: HermiT classification time, ABox consistency time, SPARQL median per ACQ class.
4. Run `validation/scripts/b2cco-oops-check.sh` against `b2-cco-base.ttl + b2-cco-maritime.ttl` and store the OOPS! pitfall report.
5. Generate a comparative table CSV at `results/comparison-dmfo-vs-b2cco.csv` with rows = ACQ, columns = DMFO status, B2-CCO status, B2-CCO diagnosis.

**Status report after step 7:** all numbers in results JSONs, OOPS! report attached.

### Step 8 — Manuscript-ready outputs (stop and review)

Produce three artefacts ready to drop into the paper:

1. `docs/manuscript-block-b2cco.md`: the half-page B2-CCO description for Section 4.2 of the paper. Includes the Faithful-Translation-Rule, the slot-mapping summary (as compact table), and a forward reference to results.
2. `docs/manuscript-table-3-extended.md`: extended Table 3 (DMFO, B1, B2-CCO) with the diagnostic column added.
3. `docs/manuscript-appendix-b2cco-diagnosis.md`: the per-ACQ diagnosis appendix material.

All three are written in Markdown for now; LNCS-LaTeX conversion happens later.

### Step 9 — Food profile (only if Maritime is fully done and time allows)

Repeat steps 4–7 for the Food domain, with one extra wrinkle: split/merge identity transformations in CCO. The DMFO version uses PROV-O `wasDerivedFrom` chains; CCO has no native PROV-O integration, so an additional ADR-006 will be needed before implementation. **Do not start step 9 without explicit confirmation.**

## Communication protocol

- After each "stop and review" point, post a status summary with: completed checklist, diffs/files created, open questions, blockers.
- For ontological modelling decisions outside the steps' explicit scope, **do not improvise** — list them as open questions and wait for me.
- For tooling/setup issues (HermiT not found, network access blocked), attempt the standard fix once, report if it fails.
- Use German or English in commit messages — match the surrounding repo. Doc files and ADRs are in English (manuscript language).

## Checklist before declaring B2-CCO complete

- [ ] All five ADRs written and reviewed
- [ ] Slot-mapping table fully populated with verified CCO 2.0 IRIs
- [ ] Base ontology classifies under HermiT, no unsatisfiable classes
- [ ] Maritime profile + ABox classifies, ABox triple count documented
- [ ] All 20 ACQs translated and classified, SPARQL queries runnable
- [ ] `results/b2-cco-results.json` and `results/b2-cco-perf.json` present
- [ ] OOPS! pitfall report stored
- [ ] Three manuscript-ready Markdown blocks in `docs/`
- [ ] `docs/abox-translation-maritime.md` shows side-by-side diff
- [ ] Faithful-Translation-Rule violations: zero
- [ ] No DMFO files modified
- [ ] Repo builds in Docker (`docker build` succeeds, `tests/run-all.sh` passes)

## Reference list (for citations in ADRs)

- Jensen, M., De Colle, G., Kindya, S., More, C., Cox, A.P., Beverley, J. (2024). *The Common Core Ontologies*. Proc. FOIS 2024. — primary CCO reference, **must be cited in every ADR**.
- CCO GitHub (CommonCoreOntology/CommonCoreOntologies), v2.0+ — opaque IRI mapping.
- Smith, B., Arp, R., Spear, A.D. (2015). *Building Ontologies with Basic Formal Ontology*. MIT Press. — for BFO continuant/occurrent commitments.
- The DMFO paper draft (in `<repo-root>/paper/`) — for the ACQ catalogue and original DMFO modelling.

## Out of scope

- Re-engineering DMFO. B2-CCO is a baseline, not a refactor.
- Optimising B2-CCO to maximise ACQ score. The goal is faithful CCO modelling, not winning a benchmark.
- Implementing PROV-O/SOSA/GeoSPARQL integration *into* CCO as a permanent extension. ADR-003 variant (a) is a documented, isolated co-import for the evaluation only.
- LLM-baseline (B2-LLM). That is a separate task.
- IRR study on the ACQ catalogue. Separate task.