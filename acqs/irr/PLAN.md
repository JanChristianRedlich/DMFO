# Inter-rater Reliability Plan (ACQ Catalogue)

This document specifies the inter-rater reliability (IRR) protocol
referenced in Paper §4.2 ("Inter-rater reliability protocol"). The
protocol, materials, and adjudication procedure are committed to the
repository before the study runs.

> **Submission status (2026-05).** The submitted version is a
> **single-annotator** catalogue (one ontology engineer). The IRR
> study below is executed before the camera-ready release following
> the protocol committed here.

---

## Annotation target

Each ACQ in `acqs/catalogue.md` is annotated with
two labels:

1. **Dimensional signature** — the set of bridges traversed,
   ⊆ {A2, A3, A4, A5, A6, identity-derivation}, plus the explicit
   marker `identity-only` for Class-I ACQs.
2. **Inferential class** ∈ {I, II, III, IV} per the Paper §4.2
   definitions:
   * I — identity-only lookup (no inter-dimensional bridge).
   * II — single-bridge traversal (exactly one of A2–A6 is required).
   * III — multi-bridge traversal (≥ 2 bridges required).
   * IV — absence detection (`FILTER NOT EXISTS` over a missing
     bridge).

The classification is **structural**: it depends on the SPARQL
shape (number of bridge predicates traversed, presence of
`NOT EXISTS`), not on whether DMFO is the architecture in use.

---

## Annotators

| Role | Background | Selection criterion |
|---|---|---|
| A1 — ontology engineer (corresponding author) | OWL 2 + SPARQL professional, DMFO author | de-facto baseline; labels already in the catalogue. |
| A2 — independent ontology engineer | OWL 2 + SPARQL professional, *not* a DMFO co-author | recruited via the W3C Semantic Web mailing list and the FOIS community. |
| A3 — domain expert (maritime + food) | port logistics or food-supply-chain SME, has read GS1 EPCIS 2.0 + IMO FAL or FDA FSMA-204 | recruited via the EU FoodChain.eu network and the maritime ISO TC 8 working group. |

A2 and A3 are blinded to:

* the DMFO axiom set (they receive only the ACQ text + standard
  citation, not the SPARQL bodies),
* the corresponding author's labels (provided post-hoc only for the
  adjudication round),
* the existence of the B1/B2 ablations.

---

## Subsample

A **30 % random subsample** of the catalogue is annotated:
⌈0.3 · 20⌉ = **6 ACQs**. The IDs are drawn once, with seed `iswc-2026`,
from `numpy.random.default_rng` (script:
[`validation/scripts/irr_sample.py`](../../validation/scripts/irr_sample.py),
to be added with the camera-ready release).

The sample is stratified across classes so that at least one ACQ from
each of Classes I, II, III, IV is in the subsample (otherwise the κ
estimate for under-represented classes is undefined). The expected
draw is one ACQ from Class I, two from Class II, two from Class III,
one from Class IV.

The selected IDs (planned, contingent on rerun with the published
seed) are documented in
`acqs/irr/sample-ids.csv` (placeholder for the camera-ready commit).

---

## Materials given to A2 / A3

* The full ACQ text (the natural-language framework-level question,
  not the SPARQL).
* The cited source standard with the relevant clause.
* A one-page **classification cheat-sheet** with one positive and one
  negative example per class (see *Cheat-sheet skeleton* below).
* The list of six bridges A2–A6 + identity-derivation, each with a
  one-sentence informal description and one positive example. **No**
  axiom statements, **no** SPARQL.

What is **withheld**:

* The DMFO TBox.
* The B1 / B2-CCO catalogues.
* The corresponding author's labels.
* The fact that the ACQ counts are saturating at 20.

---

## Cheat-sheet skeleton (annotator briefing, one page)

> **Class I** (identity-only): the question can be answered by
> checking the persistent identifier of one entity at one point in
> time. *Positive example*: "Does container CTU-1234 exist in the
> registry?" *Negative example*: "Has CTU-1234 ever been observed
> outside its declared zone?" (this would be Class III / IV).
>
> **Class II** (single-bridge): the question requires *exactly one*
> step from a state assertion to one of {activity, evidence, regime,
> zone}. *Positive example*: "What activity generated the current
> state of CTU-1234?" *Negative example*: "What activity was governed
> by which regime when CTU-1234 entered ISPS-zone Z?" (this is
> Class III).
>
> **Class III** (multi-bridge): the question requires composing
> ≥ 2 of the bridges A2–A6.
>
> **Class IV** (absence detection): the question is of the form
> "find every state for which a given bridge is missing".

---

## Procedure

1. A2 and A3 independently classify the 6 sampled ACQs. They
   receive only the materials in the previous section. Annotation
   is captured in
   `acqs/irr/annotations-A{2,3}.csv` with columns
   `acq_id, dimensional_signature, class, time_minutes, comments`.
   Time is captured to discourage rushed labels.
2. The corresponding-author labels (A1) are released *after* A2 and
   A3 submit, to prevent priming.
3. **Disagreement analysis.** For each ACQ on which any pair
   disagrees on either signature or class, the disagreement is
   recorded in `acqs/irr/disagreement-log.md`.
4. **Adjudication round.** The three annotators meet (video call) and
   walk through each disagreement. They are encouraged to re-classify
   if they find their original choice unjustified. The outcome is the
   **adjudicated label**. The adjudication transcript is summarised
   (no verbatim, GDPR-friendly) in `acqs/irr/adjudication-protocol.md`.
5. **Final scoring.** Two metrics are reported:
   * Pair-wise **Cohen's κ** (A1↔A2, A1↔A3, A2↔A3) for the *class*
     label, computed on the pre-adjudication labels.
   * Overall **Krippendorff's α** (nominal) on the *(signature, class)*
     pair label, also pre-adjudication.

The computation script will be
[`validation/scripts/irr_compute.py`](../../validation/scripts/irr_compute.py)
(uses `nltk.metrics` for κ and `simpledorff` for α). Output:
`validation/results/irr.json`.

---

## Expected outcome and pre-registered thresholds

* κ ≥ 0.80 ("substantial-to-perfect" agreement per Landis & Koch
  1977) is the **target**. Below 0.80 the catalogue is flagged for
  re-formulation in `acqs/catalogue.md` rather than
  reported as authoritative.
* α ≥ 0.75 on the joint (signature, class) label is the secondary
  threshold.

If post-adjudication labels diverge from the pre-adjudication
corresponding-author labels by more than two ACQs, the catalogue is
re-released with a v2.x revision and the affected SPARQL queries are
re-validated.

---

## Limitations

* n = 3 annotators is the minimum for κ-style metrics; higher n
  would require recruiting more domain experts than is practical
  for the camera-ready timeline.
* The 30 % subsample is small in absolute terms (6 ACQs); the κ
  estimate has correspondingly wide confidence intervals. We
  report a 95 % bootstrap CI alongside the point estimate.
* The classification is *structural*, so a domain expert without
  SPARQL background may need extra coaching on Class IV
  (`NOT EXISTS`) recognition. The cheat-sheet contains an
  explicit `FILTER NOT EXISTS`-shaped positive example.

---

## Schedule

The study runs **before the camera-ready release**, following the
protocol committed in this file. Outputs land in `acqs/irr/`.

