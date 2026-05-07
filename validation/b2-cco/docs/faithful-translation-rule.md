# Faithful-Translation-Rule (B2-CCO)

> *Authored from the evaluation specification in `../../evaluation.md`.
> If the manuscript draft contains a more authoritative formulation,
> replace this section with that text and re-run the ADR review.*

A B2-CCO modelling decision is **faithful** iff it satisfies all of
the following criteria. Decisions that violate any criterion must
either be rewritten or be flagged in
[`acq-translation.md`](acq-translation.md) as a translation gap, with
no implementation work-around.

## (F1) Native CCO pattern

For each of the six DMFO slots (Identity, State, Activity, Evidence,
Context, Location), B2-CCO must use a CCO 2.0 pattern that is
**already documented** in one of:

* Jensen et al. (2024). *The Common Core Ontologies* — FOIS 2024.
* "Modeling with the Common Core Ontologies 2024" (PDF in
  `vendor/cco-2.0/documentation/user-guides/`).
* The "Best Practices of Ontology Development" guide (same folder).
* A peer-reviewed paper using CCO that exhibits the pattern.

If a slot has no native CCO pendant, the modelling falls back to one
of:

* Reuse of an upstream BFO 2020 commitment (e.g. `bfo:Site`,
  `bfo:Process`, `bfo:Quality`) cited from the BFO ISO standard.
* A "documented absence" diagnosis recorded in the slot-mapping table
  with consequence stated.

The Evidence slot has no native CCO pendant and is the canonical
documented-absence case (ADR-003).

## (F2) Opaque IRIs

Every CCO entity reference must use the **CCO 2.0 opaque IRI**
(`https://www.commoncoreontologies.org/ont00000xxx`). Old-style
human-readable IRIs from CCO ≤ 1.x are forbidden. `rdfs:label` may be
attached for readability but never invented as a custom IRI.

## (F3) No typed inter-dimensional bridges

B2-CCO must not introduce object properties whose intended semantics
are "DMFO bridge in CCO clothing". The forbidden patterns include:

* A subproperty of `bfo:has participant` whose name encodes evidential
  grounding (e.g. `b2cco:isEvidencedBy`).
* A typed coupling of `cco:Process Regulation` to `bfo:process` that
  invents a new normative-framing relation.
* A subproperty of `cco:occurs at` typed to a fresh "institutional
  zone" class.

Where DMFO uses a typed bridge (A1–A6), B2-CCO must either:

* Reuse a generic CCO/BFO property (e.g. `bfo:has participant`,
  `cco:has agent`, `cco:describes`) with no domain/range narrowing
  beyond what CCO already declares.
* Use an ICE-based content-of-statement pattern (state the fact about
  the entity inside an Information Content Entity).
* Or document that the link is not natively expressible.

## (F4) ADR per decision

Every modelling decision required by F1 and F3 is recorded in
[`adr/`](adr/) following the template in
[`adr/000-template.md`](adr/000-template.md). The ADR cites a CCO
source (per F1), enumerates considered alternatives, and states the
consequence on ACQ classes.

## (F5) Diagnosis over patching

Where a CCO pattern fails an ACQ, the failure is documented in
[`acq-translation.md`](acq-translation.md) with a diagnostic
paragraph (which CCO commitment blocks the answer, which ADR is the
governing decision). Adding a typed bridge to "fix" the failure is a
violation of this rule unless the bridge is itself a documented
standard CCO pattern.

## Compliance checklist

Each B2-CCO file (TBox, ABox, query) carries a comment header
asserting `Faithful-Translation-Rule: F1, F2, F3, F4, F5 — compliant`
or noting which rules are deliberately deviated from with ADR
reference. CI grep checks this header.
