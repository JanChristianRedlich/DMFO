# DMFO Architecture

> Reference for the architectural decisions, formal properties, and
> design pattern network.

This document accompanies Sections 3–4 of the paper. It is the
implementation-side companion to the paper's architectural claims and
points readers from claim → file → reproduction step.

---

## 1. Motivation: analytical underdetermination

Persisting and fluent entities (sea containers, food batches, vessels,
sensors) maintain numerical identity invariantly while their state,
location, activity record, evidential basis, and normative context
vary. Four-dimensionalist ontologies (BFO 2.0, ISO 15926) close the
time-indexing gap but leave inter-dimensional structure architecturally
implicit. Statement-level contextualisation (RDF-star, Named Graphs)
provides assertion *carriers* but not typed semantic alignment between
State, Activity, Evidence, Context, and Location. Foundational
frameworks (BFO, gUFO, CCO) supply upper-level commitments but ship no
ready-made cross-dimensional bridge layer.

DMFO's research question (Paper §1):

> *How can time-indexed state assertions about persisting and fluent
> entities be represented in OWL 2 DL such that identity, causal
> provenance, evidential grounding, spatial-institutional location,
> and normative context remain modularly separable but jointly
> queryable across arbitrary domain ontologies?*

Hypothesis: vocabulary coverage is necessary but not sufficient. Adding
the alignment layer (A1)–(A6) raises situational answerability while
leaving the vocabulary inventory unchanged. The contribution is the
**alignment claim**, not new vocabulary.

---

## 2. Six dimensional slots

Each slot is given by an *anchor class*, the imported vocabulary it
draws on, and a binding expectation that domain ontologies must meet
to populate the slot. See Paper §3.1 / Table 1.

| Slot | Anchor | Imported vocab | Activation |
|---|---|---|---|
| Identity   | `dmfo:TimeVaryingEntity` (TVE)              | DMFO        | Mandatory |
| State      | `dmfo:Manifestation`                        | DMFO + PROV-O + DUL + SOSA via A1 | Mandatory |
| Evidence   | `sosa:Observation`                          | SOSA/SSN    | Optional  |
| Activity   | `prov:Activity`                             | PROV-O      | Optional  |
| Context    | `dul:Situation`, `dul:Description`          | DUL/DnS     | Optional  |
| Location   | `geo:Feature`                               | GeoSPARQL   | Optional  |

The State anchor and the Identity ↔ State bridge `dmfo:manifestationOf`
form the **mandatory core** (Paper Theorem 2(b): definitional rather
than conservative w.r.t. O_Id alone). The four remaining dimensional
modules and the corresponding bridge axioms are *selectively
activatable*: profiles that don't need them simply do not import them.

The orthogonality principle (Paper §3): **no dimensional content
entails membership in another dimension**. Crossing dimensions requires
explicit bridge typing — there are no implicit cross-dimensional
inferences.

---

## 3. Five bridges + alignment axioms (A1)–(A6)

Bridges are **inter-dimensional**, never within a single dimension.
This preserves orthogonality and avoids the rigid-role / temporal-
operator undecidability barrier of Wolter & Zakharyaschev (Paper §2,
§4.1 proof sketch).

```
            Identity                State                Evidence
            ────────                ─────                ────────
   dmfo:TimeVaryingEntity ──A2──▶ dmfo:Manifestation ──A3──▶ sosa:Observation
                                  (A1: prov:Entity ⊓
                                       dul:Event ⊓
                                       sosa:FeatureOfInterest)
                                       │
                                       │ A5
                                       ▼
                                  prov:Activity   (Activity)

            Context                                   Location
            ───────                                   ────────
            dul:Situation ──A4──▶ dul:Description    geo:Feature
                                                          ▲
                                                          │
                                                          A6
                                                          │
                                                  dul:Situation
```

| ID | Axiom | Function |
|---|---|---|
| A1 | `dmfo:Manifestation ⊑ prov:Entity ⊓ dul:Event ⊓ sosa:FeatureOfInterest` | state / prov / evidence anchor |
| A2 | `Domain/Range(dmfo:manifestationOf) = dmfo:Manifestation × dmfo:TimeVaryingEntity` | identity-state projection |
| A3 | `dmfo:evidencedBy ⊑ inverse(sosa:hasFeatureOfInterest)` | evidence bridge |
| A4 | `Domain/Range(dmfo:governedBy) = dul:Situation × dul:Description` | normative framing |
| A5 | `dmfo:stateWasGeneratedBy ⊑ prov:wasGeneratedBy`, typed `dmfo:Manifestation × prov:Activity` | state-activity sub-property |
| A6 | `dmfo:situatedAt ⊑ geo:sfWithin`, typed `dul:Situation × geo:Feature` | spatial-context bridge |

### The data-of-opportunity constraint

**No bridge module contains existential GCIs.** A `dmfo:Manifestation`
without a `dmfo:evidencedBy` link is a *consistent* representation, not
a modelling error. Absence is queryable (Class IV ACQs use
`FILTER NOT EXISTS`), not silent (Paper Corollary of Theorem 2). This
is enforced at parse time by `validation/scripts/validate_kb.py`
(zero existential-GCI bridges across the four optional bridges).

---

## 4. Identity-derivation patterns

Transformation-intensive contexts (food production, repackaging,
remanufacturing) lose entity identity across processing steps. DMFO
represents this via:

* **Splitting**: source α → successor identities β₁, …, βₙ via
  activity τ. Each βᵢ carries `prov:wasDerivedFrom α` and
  `prov:wasGeneratedBy τ`. The source α is marked
  `dmfo:SplitSourceIdentity`.
* **Merging**: source identities α₁, …, αₙ → β via activity τ. β
  carries `prov:wasDerivedFrom αᵢ` for each i. Each αᵢ is marked
  `dmfo:MergeSourceIdentity`. Obligation composition (strictest-
  applicable, union, negotiated) is a domain-policy decision encoded
  as a SHACL/SPARQL constraint over the merging Situation, not a
  DMFO core commitment (Paper §3.3).

**Acyclicity** is a closed-world validation constraint, *not* an OWL
property. PROV-O permits derivation cycles under open-world
semantics; DMFO requires deployed instances whose derivation graph
contains a cycle to be rejected at the SHACL layer. See
`shapes/identity-deriv-shapes.ttl`.

---

## 5. Formal properties

### 5.1 OWL 2 DL profile

DMFO uses only OWL 2 DL constructs: subclass axioms, domain/range,
sub-properties, inverses, one regular property chain (in the Activity
module), qualified cardinalities over simple roles, and DUL nominals.
No temporal operators, no concrete-domain chains, no non-simple role
cardinalities.

### 5.2 Decidability preservation (Paper Theorem 1)

**Theorem 1.** Let `O_DMFO` be constructed according to the alignment
axioms in Supplemental Appendix A. For any activated subset
`A ⊆ {Id, St, Lo, Act, Co, Ev}`, `O_DMFO` is a decidable OWL 2 DL
ontology with combined complexity in 2-NEXPTIME.

The construction is closed against all four SROIQ(D)-undecidability
patterns of Wolter & Zakharyaschev — see Paper §4.1 proof sketch.

### 5.3 Compositional safety (Paper Theorem 2)

**Theorem 2(a).** For every optional dimensional module Oⱼ with
j ∈ {Lo, Act, Co, Ev} and every optional bridge module, locality-based
checks classify the module as a *conservative extension* of Σ* with
respect to the prior DMFO signature, established per axiom via
top-locality.

**Theorem 2(b).** `O_bridge(a,b) ∪ O_St` is a *definitional extension*
of `O_Id`: exactly two axioms fail top-locality because they
architecturally require constraining `dmfo:Manifestation` as a
time-indexed state-bearing entity. These are A1 and A2.

**Theorem 2(c).** All optional bridge modules contain no existential
GCIs.

Reproduction: `python validation/scripts/locality_check.py` produces
the per-module classification table that matches the paper's
Appendix A §§A.1–A.13.

### 5.4 Module extractability (Paper Proposition 3)

For any signature Σ corresponding to an activated subset A, the
Σ-locality-based module `M_Σ(O_DMFO)` is computable in polynomial time
in `|O_DMFO|`. This is a direct application of Cuenca Grau et al.
(2008) Theorem 2 given the top-locality classification of Theorem 2(a).

---

## 6. Disjoint design responsibilities (P1, P2, P3)

* **(P1) Open-world inference is OWL.** A constraint that should
  propagate across imports, participate in classification, or be
  necessary for query-path availability is stated as an OWL axiom.
  The six alignment axioms are all of this kind.
* **(P2) Closed-world validation is SHACL.** A constraint that must
  reject deployment-time data not satisfying a profile, but must not
  turn into an open-world entailment, is a SHACL shape. The
  acyclicity constraint on identity derivation is the canonical
  example.
* **(P3) No SHACL substitution for OWL inference.** SHACL constraints
  never relax OWL claims, only refine them under a closed-world
  assumption. The conservativity and locality results therefore apply
  to (A1)–(A6) only; SHACL shapes are deployment artefacts, not part
  of the formal alignment layer.

---

## 7. Cross-references

| Paper section | Repo artefact |
|---|---|
| §3.1 (six slots) | [ontology/dmfo-*.ttl](../../ontology/) |
| §3.2 / Table 1 (A1–A6) | [docs/specifications/ALIGNMENT_AXIOMS.md](../specifications/ALIGNMENT_AXIOMS.md) |
| §3.3 (identity derivation) | [ontology/dmfo-identity-deriv.ttl](../../ontology/dmfo-identity-deriv.ttl), [shapes/identity-deriv-shapes.ttl](../../shapes/identity-deriv-shapes.ttl) |
| §3.4 / Listing 1 (worked example) | [profiles/maritime/](../../profiles/maritime/) |
| §4.1 / Theorem 2 (locality) | [validation/scripts/locality_check.py](../../validation/scripts/locality_check.py) |
| §4.2 / Table 3 (ACQ ablation) | [validation/scripts/run_all_acqs.py --all](../../validation/scripts/run_all_acqs.py) |
| §4.3 / Table 4 (negative cases) | [shapes/dmfo-core-shapes.ttl](../../shapes/dmfo-core-shapes.ttl) (severities) |
| §4.4 (profile authoring) | [docs/specifications/PROFILE_AUTHORING.md](../specifications/PROFILE_AUTHORING.md) |
| §6 (data + code availability) | [Dockerfile](../../Dockerfile), [.github/workflows/ci.yml](../../.github/workflows/ci.yml) |
