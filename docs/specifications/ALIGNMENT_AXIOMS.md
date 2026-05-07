# Alignment Axioms (A1)–(A6)

The six alignment axioms are the formal content of the DMFO contribution
(Paper §3.2, Table 1). Each is stated below in three forms: Manchester
syntax (the form a profile author would type into Protégé), the Turtle
form actually shipped in `ontology/`, and the locality classification
that the reproduction package verifies.

---

## A1 — State / PROV / Evidence anchor

**Manchester:**

```
Class: dmfo:Manifestation
  SubClassOf: prov:Entity and dul:Event and sosa:FeatureOfInterest
```

**Turtle** ([`ontology/dmfo-state.ttl`](../../ontology/dmfo-state.ttl)):

```turtle
dmfo:Manifestation
    rdfs:subClassOf [
        a owl:Class ;
        owl:intersectionOf ( prov:Entity dul:Event sosa:FeatureOfInterest )
    ] .
```

**Locality:** **definitional** (Paper Theorem 2(b)). A1 imposes joint
typing of a fresh class (`dmfo:Manifestation`) over three classes from
the prior signature; this is the State anchor commitment that cannot be
factored out as a conservative extension of `O_Id` alone.

**Permissivity argument** (Paper §3.2): each of the three super-classes
is *itself permissive* (PROV's `prov:Entity` deliberately does not
commit to endurant/perdurant; DUL's `dul:Event` is perdurant; SOSA's
`sosa:FeatureOfInterest` is a role, not a category). The intersection
is therefore a permissive strengthening, not a category violation.
HermiT classifies the joint typing without flagging unsatisfiability
(reproduce: `python validation/scripts/run_hermit_reasoner.py --tbox-only`).

---

## A2 — Identity-State projection

**Manchester:**

```
ObjectProperty: dmfo:manifestationOf
  Domain: dmfo:Manifestation
  Range:  dmfo:TimeVaryingEntity
```

**Turtle** ([`ontology/dmfo-state.ttl`](../../ontology/dmfo-state.ttl)):

```turtle
dmfo:manifestationOf
    a owl:ObjectProperty ;
    rdfs:domain dmfo:Manifestation ;
    rdfs:range  dmfo:TimeVaryingEntity .
```

**Locality:** **definitional** (Paper Theorem 2(b)). The typed range on
`dmfo:TimeVaryingEntity` (which is in O_Id, the prior context) imposes a
non-trivial commitment that fails top-locality.

A2 is the canonical Identity-State bridge: every Manifestation is
projected onto exactly one TVE (functional from the State side).

---

## A3 — Evidence bridge

**Manchester:**

```
ObjectProperty: dmfo:evidencedBy
  Domain: dmfo:Manifestation
  Range:  sosa:Observation
  SubPropertyOf: inverse sosa:hasFeatureOfInterest
```

**Turtle** ([`ontology/dmfo-evidence.ttl`](../../ontology/dmfo-evidence.ttl)):

```turtle
dmfo:evidencedBy
    a owl:ObjectProperty ;
    rdfs:domain dmfo:Manifestation ;
    rdfs:range  sosa:Observation ;
    rdfs:subPropertyOf [ owl:inverseOf sosa:hasFeatureOfInterest ] .
```

**Locality:** top-local. A3 introduces a fresh property with imported
vocabulary on the right-hand side; under the top-locality criterion,
fresh-property axioms with no other fresh symbols are top-local
(Cuenca Grau et al. 2008).

A3 is *optional*: a Manifestation without an `dmfo:evidencedBy` link is
a consistent representation. The absence is queryable via
[ACQ-IV-01](../../acqs/queries/dmfo/ACQ-IV-01_evidence_gap.sparql).

---

## A4 — Normative framing

**Manchester:**

```
ObjectProperty: dmfo:governedBy
  Domain: dul:Situation
  Range:  dul:Description
```

**Turtle** ([`ontology/dmfo-context.ttl`](../../ontology/dmfo-context.ttl)):

```turtle
dmfo:governedBy
    a owl:ObjectProperty ;
    rdfs:domain dul:Situation ;
    rdfs:range  dul:Description .
```

**Locality:** top-local.

A4 couples a contextual situation to the regime / obligation set under
which it constitutes a distinct institutional act. Multi-regime framing
is not derivable from physical description alone.

---

## A5 — State-Activity sub-property

**Manchester:**

```
ObjectProperty: dmfo:stateWasGeneratedBy
  Domain: dmfo:Manifestation
  Range:  prov:Activity
  SubPropertyOf: prov:wasGeneratedBy
```

**Turtle** ([`ontology/dmfo-activity.ttl`](../../ontology/dmfo-activity.ttl)):

```turtle
dmfo:stateWasGeneratedBy
    a owl:ObjectProperty ;
    rdfs:domain dmfo:Manifestation ;
    rdfs:range  prov:Activity ;
    rdfs:subPropertyOf prov:wasGeneratedBy .
```

**Locality:** top-local.

A5 is a DMFO sub-property, **not** a global domain restriction on
`prov:wasGeneratedBy`. Stating it as a domain restriction would infer
Manifestation membership for any imported PROV `prov:Entity` appearing
in subject position — an unintended global consequence over external
PROV data. The sub-property construction localises the state-coupling
commitment to the DMFO layer (Paper §3.2 "PROV contamination").

---

## A6 — Spatial-Context bridge

**Manchester:**

```
ObjectProperty: dmfo:situatedAt
  Domain: dul:Situation
  Range:  geo:Feature
  SubPropertyOf: geo:sfWithin
```

**Turtle** ([`ontology/dmfo-location.ttl`](../../ontology/dmfo-location.ttl)):

```turtle
dmfo:situatedAt
    a owl:ObjectProperty ;
    rdfs:domain dul:Situation ;
    rdfs:range  geo:Feature ;
    rdfs:subPropertyOf geo:sfWithin .
```

**Locality:** top-local.

A6 fixes the typed bridge from contextual situations to spatial
features. Institutional zone membership is constituted by **decision**,
not by geometric containment; A6 leverages GeoSPARQL spatial relations
through the `geo:sfWithin` super-property without committing the
framework to a containment ontology.

---

## ACQ-minimality

Each axiom contributes one missing cross-dimensional typing or bridge
relation. The B1 ablation in
[`validation/scripts/run_all_acqs.py`](../../validation/scripts/run_all_acqs.py)
(invoked with `--all`) confirms that removing A1–A6 from the ABox layer
eliminates 11–12 of the 20 ACQs depending on instantiation, with each
loss mechanically attributable to a specific axiom (failure-pattern
attribution per Paper §4.2).

| Lost ACQ class | Failing axiom |
|---|---|
| Class III multi-bridge accountability | A1 + A5 |
| Evidence-grounded queries | A3 |
| Normative-framing queries | A4 |
| Location-scoped obligation queries | A6 |
| Identity-derivation queries | A1 + identity-deriv module |
