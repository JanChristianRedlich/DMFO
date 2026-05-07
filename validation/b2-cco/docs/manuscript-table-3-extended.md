# Manuscript Table 3 — Extended (DMFO, B1, B2-CCO×2)

> Extension of Paper Table 3 with **two** B2-CCO variants and a
> per-class diagnostic column. Replaces the camera-ready TODO. Numbers
> from `validation/b2-cco/results/b2-cco-results-{maritime,food}{,-native}.json`
> and `validation/results/queries_{maritime,food}.json`.

## Why two B2-CCO variants?

Faithful-Translation-Rule **F1** demands that every B2-CCO slot use a
CCO 2.0 pattern documented in Jensen et al. 2024 or the *Modeling
with CCO* guide. SOSA/SSN is **not** part of CCO 2.0. ADR-003a
co-imports SOSA as a documented exception "for evaluation only";
ADR-003b is the strict CCO-native alternative using
`cco:Measurement Information Content Entity` + `cco:is about` only.

We therefore report two B2-CCO scores:

* **B2-CCO/sosa** — ADR-003a active. Treats SOSA as a temporary
  upstream import, lets the four evidence-related ACQs use SOSA's
  native bitemporal + sensor properties.
* **B2-CCO/native** — strict CCO-native (ADR-003b only). No SOSA
  imports; ACQ-II-03 + ACQ-IV-01 are rewritten over Measurement ICE +
  `cco:is_about`; ACQ-II-06 (bitemporal completeness) and ACQ-III-03
  (sensor link) become structurally underdetermined under CCO 2.0.

The native column is the F1-conformant baseline; the SOSA column is
an upper bound on what a CCO-based architecture achieves with one
disciplined upstream borrow.

## Table 3. Controlled alignment ablation, by ACQ dimension group.

`✓` = fully answerable · `◑` = partial / semantically shifted /
vacuously empty · `✗` = structurally underdetermined.

### Per-instantiation scores

| Framework | Maritime | Food | Combined (any-profile-answers) |
|---|---|---|---|
| **DMFO** | **20/20** | 20/20 | **20/20** |
| **B1 (DMFO − A1–A6)** | 8/20 | 8/20 | 8/20 |
| **B2-CCO/sosa** (ADR-003a SOSA co-import) | 17/20 | 17/20 | **17/20** |
| **B2-CCO/native** (ADR-003b strict CCO-native) | 15/20 | 15/20 | **15/20** |

### Per-class breakdown

| Framework | Profile | Class I | Class II | Class III | Class IV | Total |
|---|---|---|---|---|---|---|
| DMFO       | maritime | 2/2 | 6/6 | 8/8 | 4/4 | 20/20 |
| DMFO       | food     | 2/2 | 6/6 | 8/8 | 4/4 | 20/20 |
| B1         | maritime | 2/2 | 4/6 | 2/8 | 0/4 | 8/20 |
| B1         | food     | 2/2 | 4/6 | 2/8 | 0/4 | 8/20 |
| B2-CCO/sosa | maritime | 2/2 | 6/6 | 6/8 | 3/4 | 17/20 |
| B2-CCO/sosa | food     | 2/2 | 6/6 | 6/8 | 3/4 | 17/20 |
| B2-CCO/native | maritime | 2/2 | 5/6 | 5/8 | 3/4 | 15/20 |
| B2-CCO/native | food     | 2/2 | 5/6 | 5/8 | 3/4 | 15/20 |

The two instantiations now score **identically** under all
frameworks, because the LCL deconsolidation scenario added to the
maritime ABox (UN/CEFACT MMT, IMO FAL.5/Circ.42 §3.5) exercises the
same identity-derivation pattern that food's split / merge scenario
does. ACQ-III-05 + ACQ-III-08 are therefore now answered by both
instantiations under DMFO, and by both under B2-CCO via ADR-006's
act-mediated chain.

### Per-ACQ diagnostic column (combined view)

| ACQ | DMFO mar | DMFO food | sosa mar | sosa food | native mar | native food | Diagnosis ADR |
|---|---|---|---|---|---|---|---|
| ACQ-I-01   | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-001 |
| ACQ-I-02   | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-001+003a |
| ACQ-II-01  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-001 |
| ACQ-II-02  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-002 |
| ACQ-II-03  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-003a/b — Measurement ICE works for FoI substitute |
| ACQ-II-04  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-005 |
| ACQ-II-05  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-004 |
| ACQ-II-06  | ✓ | ✓ | ✓ | ✓ | **✗** | **✗** | ADR-003b — no bitemporal phenomenon/result-time in CCO Measurement ICE |
| ACQ-III-01 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-001+002 |
| ACQ-III-02 | ✓ | ✓ | ◑ | ◑ | ◑ | ◑ | ADR-004 — Situation reified as Act loses multi-state inclusion |
| ACQ-III-03 | ✓ | ✓ | ✓ | ✓ | **✗** | **✗** | ADR-003b — no sensor concept in CCO |
| ACQ-III-04 | ✓ | ✓ | **✗** | **✗** | **✗** | **✗** | ADR-002 — strict reading of PROV-O §5.7 (`qualifiedUsage` + `hadRole`); no CCO analogue of `prov:Role` |
| ACQ-III-05 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-006 — act-mediated derivation; both profiles exercise it (LCL deconsolidation in maritime, splitting/merging in food) |
| ACQ-III-06 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-004+005 |
| ACQ-III-07 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-002+005 |
| ACQ-III-08 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-006 — transitive `(^has_output/has_input)+` chain |
| ACQ-IV-01  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-003a/b — NOT EXISTS works for both |
| ACQ-IV-02  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-002 |
| ACQ-IV-03  | ✓ | ✓ | ◑ | ◑ | ◑ | ◑ | ADR-001 — scheme implicit in ICE class |
| ACQ-IV-04  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADR-004 |

The only difference between B2-CCO/sosa and B2-CCO/native columns is
on **ACQ-II-06** (observation completeness, bitemporal) and
**ACQ-III-03** (state→evidence→sensor) — both downgrade from ✓ to ✗
when SOSA is unavailable.

## Reading guide

* **DMFO 20/20 combined.** The combined Maritime + Food catalog
  answers all 20 ACQs (ACQ-III-05, ACQ-III-08 are answered by Food).
* **B2-CCO/sosa 17/20 combined.** With one disciplined upstream
  borrow (SOSA), CCO reaches within 3 ACQs of DMFO. The unanswered
  ACQs are **ACQ-III-02**, **ACQ-III-04** and **ACQ-IV-03**.
* **B2-CCO/native 15/20 combined.** Without the SOSA fallback the
  CCO-native architecture loses 5 ACQs vs. DMFO — adding
  **ACQ-II-06** and **ACQ-III-03** to the gap because CCO has no
  bitemporal observation pattern and no sensor concept.
* **B1 (DMFO − A1–A6)** collapses to 8/20. The alignment-axiom
  ablation confirms Paper §4.2's hypothesis: vocabulary co-import
  without the typed bridges is empirically insufficient.

The decisive Δ between **DMFO and B2-CCO/native** is concentrated in
five ACQs, each attributable to a specific ADR:

| ACQ | DMFO ✓ → CCO/native | Architecturally costs… |
|---|---|---|
| ACQ-II-06 | ✓ → ✗ | bitemporal data quality (ISO 8000-61): no phenomenon/result-time split in CCO |
| ACQ-III-02 | ✓ → ◑ | DnS Situation pattern: multi-state inclusion under one situation |
| ACQ-III-03 | ✓ → ✗ | sensor concept: SOSA `madeBySensor` has no CCO analogue |
| ACQ-III-04 | ✓ → ✗ | qualified causal-information traversal (PROV-O §5.7): no `prov:Role` analogue in CCO |
| ACQ-IV-03 | ✓ → ◑ | identifier-scheme attribute vs. ICE-class typing |

Each of these architectural costs maps to a single ADR (003b, 004,
003b, 002, 001 respectively).

## Reading guide for camera-ready

The story for the manuscript is now: B2-CCO is a *non-tautological*
baseline that demonstrates **architectural costs** of choosing the
BFO/CCO foundation:

1. **The DnS Situation pattern has no faithful CCO equivalent**
   (ADR-004 → ACQ-III-02). Multi-state inclusion under a single
   contextual frame is not natively expressible.
2. **PROV-O is an isolated upstream commitment for CCO** (ADR-002 →
   ACQ-III-04). Causal-information traversal degrades to temporal
   precedence.
3. **SOSA/SSN is an isolated upstream commitment for CCO** (ADR-003 →
   ACQ-II-06 + ACQ-III-03). The bitemporal observation pattern and
   the sensor concept have no CCO-native counterparts; the strict
   B2-CCO/native variant therefore loses both ACQs.
4. **Identifier-scheme attribute vs. ICE-class typing** (ADR-001 →
   ACQ-IV-03) is a minor but documented semantic shift.
5. **Identity-derivation is *not* a structural advantage of DMFO**.
   With ADR-006 in place, B2-CCO answers ACQ-III-05 and ACQ-III-08;
   the DMFO advantage is ergonomic (½ the SPARQL length).

The honest reading is: when DMFO co-imports four upstream vocabularies
(PROV-O, SOSA/SSN, DUL/DnS, GeoSPARQL) and bridges them with six
typed alignment axioms, it answers all 20 standard-derived ACQs.
A faithful CCO-native alternative — one that respects CCO 2.0's
documented commitments and refuses to back-port the upstream
vocabularies — answers 16/20. The 4-ACQ gap is exactly the cost of
*not* importing PROV-O / SOSA / DnS-style situations into a BFO-only
foundation.
