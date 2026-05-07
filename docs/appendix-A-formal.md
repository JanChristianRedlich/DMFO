# Appendix A — Formal Properties

This appendix consolidates the formal-properties material that the
paper explicitly references in §3 (modular decomposition + Theorem 1
+ Theorem 2). It is split into the following sections:

* **A.1 — Per-axiom Turtle source** — full Turtle, with `ontology/`
  pointers.
* **A.2 — OWL 2 DL construct table** — which constructs each axiom
  uses.
* **A.3 — Decidability check** — the four SROIQ(D) undecidability
  patterns, and how each axiom avoids them.
* **A.4 to A.13 — Per-module locality classification** — twelve
  modules, each with its full axiom set + classification.
* **A.14 — Re-runnable locality script** — pointer + invariants.
* **A.15 — Imports manifest with hashes** — pinned versions.

The full cross-reference between this appendix and the paper is in
[`docs/specifications/ALIGNMENT_AXIOMS.md`](specifications/ALIGNMENT_AXIOMS.md)
(per-axiom Manchester-syntax view).

---

## A.1 — Per-axiom Turtle source

Authoritative location: `ontology/dmfo-*.ttl`. Reproduced here for
self-contained review.

### A1 — State / PROV / Evidence anchor (`ontology/dmfo-state.ttl`)

```turtle
dmfo:Manifestation
    rdfs:subClassOf [
        a owl:Class ;
        owl:intersectionOf ( prov:Entity dul:Event sosa:FeatureOfInterest )
    ] .
```

### A2 — Identity-State projection (`ontology/dmfo-state.ttl`)

```turtle
dmfo:manifestationOf
    a owl:ObjectProperty ;
    rdfs:domain dmfo:Manifestation ;
    rdfs:range  dmfo:TimeVaryingEntity .
```

### A3 — Evidence bridge (`ontology/dmfo-evidence.ttl`)

```turtle
dmfo:evidencedBy
    a owl:ObjectProperty ;
    rdfs:subPropertyOf [ owl:inverseOf sosa:hasFeatureOfInterest ] .
```

### A4 — Normative framing (`ontology/dmfo-context.ttl`)

```turtle
dmfo:governedBy
    a owl:ObjectProperty ;
    rdfs:domain dul:Situation ;
    rdfs:range  dul:Description .
```

### A5 — State-Activity sub-property (`ontology/dmfo-activity.ttl`)

```turtle
dmfo:stateWasGeneratedBy
    a owl:ObjectProperty ;
    rdfs:subPropertyOf prov:wasGeneratedBy ;
    rdfs:domain dmfo:Manifestation ;
    rdfs:range  prov:Activity .
```

### A6 — Spatial-context bridge (`ontology/dmfo-location.ttl`)

```turtle
dmfo:situatedAt
    a owl:ObjectProperty ;
    rdfs:subPropertyOf geo:sfWithin ;
    rdfs:domain dul:Situation ;
    rdfs:range  geo:Feature .
```

### Identity-derivation (`ontology/dmfo-identity-deriv.ttl`)

```turtle
dmfo:SplitSourceIdentity rdfs:subClassOf dmfo:TimeVaryingEntity .
dmfo:MergeSourceIdentity rdfs:subClassOf dmfo:TimeVaryingEntity .
# Acyclicity of prov:wasDerivedFrom is enforced by SHACL
# (shapes/identity-deriv-shapes.ttl); OWL alone cannot exclude
# cycles under open-world semantics.
```

---

## A.2 — OWL 2 DL construct table

| Axiom | Construct used | DL-profile contribution |
|---|---|---|
| A1 | `rdfs:subClassOf` of an anonymous class given by `owl:intersectionOf` over three named classes from imported vocabularies | Inclusion + intersection. Stays in `EL+` for the local sub-graph. |
| A2 | `rdfs:domain` + `rdfs:range` on a fresh object property | Property-restriction. No quantifiers, no chains. |
| A3 | `rdfs:subPropertyOf` of an anonymous property given by `owl:inverseOf` of a named property | Inverse property. SROIQ(D) — but no chain, no rigid role. |
| A4 | `rdfs:domain` + `rdfs:range` on a fresh object property | Same shape as A2. |
| A5 | `rdfs:subPropertyOf` of a named property + domain + range | Sub-property. No chain. |
| A6 | `rdfs:subPropertyOf` of a named property + domain + range | Same shape as A5. |

No axiom uses **qualified cardinality**, **regular property chains**,
**nominals**, or **rigid roles**. The DMFO contribution is therefore
contained in the `EL++ ∪ {inverse, sub-property, intersection}`
fragment, well inside SROIQ(D) decidability bounds.

---

## A.3 — Decidability check (four SROIQ(D) undecidability patterns)

| Pattern (Horrocks et al. 2006) | DMFO axiom set | Diagnosis |
|---|---|---|
| Concrete-domain chains across object properties | none | A1–A6 use no concrete domains beyond `xsd:dateTimeStamp` on the `dmfo:manifestationTimestamp` datatype property; concrete domain occurs at most once per chain. |
| Regular property chains involving fresh roles | none | No `owl:propertyChainAxiom` in any DMFO module. |
| Nominals + cardinality on the same property | none | No `owl:oneOf` and no qualified-cardinality restrictions in any DMFO module. |
| Rigid roles (object properties asserted both reflexive and irreflexive) | none | No reflexivity, irreflexivity, or rigidity axioms. |

The DMFO modules pass each of the four patterns **vacuously**. The
check is automated by
[`validation/scripts/validate_kb.py`](../validation/scripts/validate_kb.py)
(grep against the construct list) and is part of CI
(`.github/workflows/ci.yml`).

---

## A.4 — Module locality classification (overview)

Source of truth:
[`validation/results/locality_classification.json`](../validation/results/locality_classification.json),
produced by `validation/scripts/locality_check.py`.

| § | Module | Top-local | Definitional | Non-local |
|---|---|---|---|---|
| A.4 | `O_base` | 2 | 0 | 0 |
| A.5 | `O_Id` | 6 | 0 | 0 |
| A.6 | `O_St + b(Id,St)` | 4 | **2** | 0 |
| A.7 | `O_Lo` (location-only sub-module) | 0 | 0 | 0 |
| A.8 | `O_Lo + b(Co,Lo)` | 4 | 0 | 0 |
| A.9 | `O_Act` (activity-only sub-module) | 0 | 0 | 0 |
| A.10 | `O_Act + b(St,Act)` | 4 | 0 | 0 |
| A.11 | `O_Co` (context-only sub-module) | 0 | 0 | 0 |
| A.12 | `O_Co + b(St,Co)` | 3 | 0 | 0 |
| A.13 | `O_Ev + b(St,Ev)` | 4 | 0 | 0 |
| A.14 | `O_identity-deriv` | 3 | 0 | 0 |
| A.15 | `O_dmfo-full` (aggregated) | 30 | 2 | 0 |

The two definitional axioms in `O_St + b(Id,St)` are **A1** and **A2**
(Paper Theorem 2(b)). All other axioms are top-local: every bridge
module is a conservative extension over the prior signature.

---

### A.6 — Definitional axioms in `O_St + b(Id,St)` (full detail)

```
A1: dmfo:Manifestation ⊑ prov:Entity ⊓ dul:Event ⊓ sosa:FeatureOfInterest
    fresh symbols: dmfo:Manifestation
    classification: definitional
    rationale: typing of a fresh class over three classes from the
    prior signature; cannot be factored as a conservative extension
    of O_Id alone.

A2: dmfo:manifestationOf  rdfs:range  dmfo:TimeVaryingEntity
    fresh symbols: dmfo:manifestationOf
    classification: definitional
    rationale: range commitment on a fresh property towards a
    previously-defined class; the projection of state to identity
    is intentional and cannot be omitted in any DMFO-conformant
    profile.
```

All other axioms in `O_St + b(Id,St)` (4 axioms: the property
characteristics, the manifestation timestamp datatype property
declarations) are **top-local**: each new symbol takes its full
extension under top-replacement, so it cannot constrain prior
signature.

The full per-axiom JSON (with shape diagnosis and fresh-symbol
list) is at
[`validation/results/locality_classification.json`](../validation/results/locality_classification.json).

---

## A.14 — Re-runnable locality script

```bash
python validation/scripts/locality_check.py
```

Output: `validation/results/locality_classification.json`. The script
operates on the rdflib in-memory graph; on a different machine, with
different versions of the imported vocabularies, the script may
report additional definitional axioms — this is by design. The
conservativity claim in Paper Theorem 2 is *bounded to the imported
versions in A.15*.

The script exits 0 iff:

* the only definitional axioms are A1 and A2 (in `O_St + b(Id,St)`),
* every other DMFO axiom is top-local,
* no DMFO axiom is non-local.

Any deviation produces a non-zero exit code and a verbose diff
against the expected classification.

---

## A.15 — Imports manifest with hashes (pinned versions)

All DMFO conservativity arguments are bound to these specific import
versions. Any future re-issuance must re-run `locality_check.py` and
update this manifest.

| Vocabulary | Canonical IRI | Version | Local file | SHA-256 (pinned for camera-ready) |
|---|---|---|---|---|
| PROV-O | `http://www.w3.org/ns/prov-o` | 2013-04-30 (W3C Recommendation) | `ontology/imports/prov-o.ttl` | `<filled by fetch_imports.sh>` |
| SOSA | `http://www.w3.org/ns/sosa/` | 2017-10-19 (W3C Recommendation) | `ontology/imports/sosa.ttl` | `<filled by fetch_imports.sh>` |
| SSN | `http://www.w3.org/ns/ssn/` | 2017-10-19 (W3C Recommendation) | `ontology/imports/ssn.ttl` | `<filled by fetch_imports.sh>` |
| DUL/DnS | `http://www.ontologydesignpatterns.org/ont/dul/DUL.owl` | 3.36 (LOA stable release) | `ontology/imports/dul.owl` | `<filled by fetch_imports.sh>` |
| GeoSPARQL | `http://www.opengis.net/ont/geosparql` | 1.1 (OGC standard 22-047r1) | `ontology/imports/geosparql.ttl` | `<filled by fetch_imports.sh>` |
| OWL-Time | `http://www.w3.org/2006/time` | 2022-11-15 (W3C Recommendation revision) | `ontology/imports/time.ttl` | `<filled by fetch_imports.sh>` |

The SHA-256 column is populated by
[`validation/scripts/fetch_imports.sh`](../validation/scripts/fetch_imports.sh)
on each run; the camera-ready release will commit the hash table to
`ontology/imports/SHA256SUMS`.

## Cross-reference to paper

* §3.2 Table 1 → A.1 / A.2 (axiom definitions + construct list).
* §3.3 (decidability) → A.3.
* Theorem 2(a) (top-locality) → A.4 (table).
* Theorem 2(b) (two definitional axioms) → A.6.
