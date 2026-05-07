# Appendix D — Worked Examples + Component-Necessity Matrix

This appendix consolidates the worked-example material referenced in
Paper §3.2–§3.3 + §4.2. It is split into:

* **D.1** — Abstract pattern (one Manifestation, all five bridges).
* **D.2** — Maritime-profile binding (full Turtle, sample ABox).
* **D.3** — Food-traceability profile binding (full Turtle, sample
  ABox).
* **D.4** — Identity-derivation pattern: split.
* **D.5** — Identity-derivation pattern: merge.
* **D.6** — Strictest-applicable-obligation composition.
* **D.7** — Component-necessity matrix (per module/bridge × per ACQ).

The full ABoxes are in `profiles/maritime/mar-abox.ttl` and
`profiles/food/food-abox.ttl`; this appendix excerpts the load-bearing
fragments and explains them.

---

## D.1 — Abstract pattern: one Manifestation, all five bridges

```turtle
@prefix dmfo: <https://w3id.org/dmfo#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix dul:  <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#> .
@prefix geo:  <http://www.opengis.net/ont/geosparql#> .
@prefix ex:   <https://w3id.org/dmfo/example#> .

ex:Entity_001     a dmfo:TimeVaryingEntity ;
                  dmfo:hasIdentifier "ID-001" .

ex:M_InYard       a dmfo:Manifestation, prov:Entity, dul:Event,
                    sosa:FeatureOfInterest ;
                  dmfo:manifestationOf       ex:Entity_001 ;          # A2
                  dmfo:stateWasGeneratedBy   ex:Activity_Arrival ;    # A5
                  dmfo:evidencedBy           ex:Observation_AIS ;     # A3
                  dmfo:manifestationTimestamp "2026-04-15T08:30:00Z"^^xsd:dateTimeStamp .

ex:Sit_001        a dul:Situation ;
                  dul:hasSetting             ex:M_InYard ;
                  dmfo:governedBy            ex:Regime_ISPS ;         # A4
                  dmfo:situatedAt                ex:Zone_Yard1 .          # A6

ex:Activity_Arrival a prov:Activity .
ex:Observation_AIS  a sosa:Observation ;
                    sosa:hasFeatureOfInterest ex:M_InYard .
ex:Regime_ISPS      a dul:Description .
ex:Zone_Yard1       a geo:Feature .
```

This nine-statement pattern triggers all five bridges (A2 through A6).
A1 is satisfied implicitly by `ex:M_InYard a dmfo:Manifestation,
prov:Entity, dul:Event, sosa:FeatureOfInterest` (the joint typing
required by the anchor sub-class axiom).

The corresponding SPARQL — "what activity generated the in-yard
state of ID-001 under what regime, in which zone, evidenced by
what observation?" — traverses A2 + A3 + A4 + A5 + A6 in one go.
This is the maximal Class-III ACQ and is structurally equivalent
to ACQ-III-07 (air-record visibility, IATA ONE Record).

---

## D.2 — Maritime-profile binding (excerpt)

Full source: [`profiles/maritime/mar-tbox.ttl`](../profiles/maritime/mar-tbox.ttl)
+ [`profiles/maritime/mar-abox.ttl`](../profiles/maritime/mar-abox.ttl).

### TBox (slot bindings)

```turtle
mar:Container             rdfs:subClassOf dmfo:TimeVaryingEntity .
mar:InYard                rdfs:subClassOf dmfo:Manifestation .
mar:CraneTransfer         rdfs:subClassOf prov:Activity .
mar:ISPSZone              rdfs:subClassOf geo:Feature .
mar:Observation_AIS       rdfs:subClassOf sosa:Observation .
mar:CustodyTransferSituation
                          rdfs:subClassOf dul:Situation .
mar:RegulatedZone         rdfs:subClassOf dul:Description .
mar:CargoLot              rdfs:subClassOf dmfo:TimeVaryingEntity .
mar:DeconsolidationActivity rdfs:subClassOf prov:Activity .
```

Each binding pins one anchor class. The profile remains a
*conservative extension* of the DMFO core because the bindings only
*sub-class* anchor classes; no new bridge property is introduced
(F3-equivalent prohibition).

### ABox (port-call sequence, abridged)

```turtle
ex:CTU_1234           a mar:Container ;
                      dmfo:hasIdentifier "CSQU3054383" ;       # GS1 SSCC

ex:CraneTransfer_002  a mar:CraneTransfer ;
                      prov:startedAtTime "2026-04-15T08:30:00Z"^^xsd:dateTimeStamp ;
                      prov:endedAtTime   "2026-04-15T08:42:00Z"^^xsd:dateTimeStamp ;
                      prov:wasAssociatedWith ex:Operator_HHLA .

ex:M_InYard_002       a mar:InYard ;
                      dmfo:manifestationOf      ex:CTU_1234 ;
                      dmfo:stateWasGeneratedBy  ex:CraneTransfer_002 ;
                      dmfo:evidencedBy          ex:AISObs_002 ;
                      dmfo:manifestationTimestamp "2026-04-15T08:42:00Z"^^xsd:dateTimeStamp .

ex:Sit_002            a mar:CustodyTransferSituation ;
                      dul:hasSetting   ex:M_InYard_002 ;
                      dmfo:governedBy  ex:ISPS_Regime_HamburgPort ;
                      dmfo:situatedAt      ex:ISPS_Zone_HamburgYard1 .
```

This fragment exercises ACQ-II-01 through ACQ-III-07 once.

LCL deconsolidation (one cargo lot split into three sub-cargo-lots)
is in the full file; it activates ACQ-III-05 + ACQ-III-08.

---

## D.3 — Food-traceability profile binding (excerpt)

Full source: [`profiles/food/food-tbox.ttl`](../profiles/food/food-tbox.ttl)
+ [`profiles/food/food-abox.ttl`](../profiles/food/food-abox.ttl).

### TBox (slot bindings)

```turtle
food:Batch              rdfs:subClassOf dmfo:TimeVaryingEntity .
food:KDE                rdfs:subClassOf dmfo:Manifestation .   # KDE = Key Data Element
food:CTE                rdfs:subClassOf prov:Activity .        # CTE = Critical Tracking Event
food:FSMARecord         rdfs:subClassOf sosa:Observation .
food:TraceabilityRegime rdfs:subClassOf dul:Description .
```

Per FDA FSMA-204 the two relevant constructs are KDE (state record)
and CTE (the activity that generated the KDE) — they map cleanly
onto Manifestation and Activity, with A5 connecting them.

### ABox (split + merge sequence, abridged)

```turtle
ex:Batch_FB001       a food:Batch ;
                     dmfo:hasIdentifier "GTIN-04012345-LOT-2026-001" .

ex:Split_001         a prov:Activity, dmfo:SplitSourceIdentity ;
                     prov:used                  ex:Batch_FB001 ;
                     prov:startedAtTime         "2026-04-15T10:00:00Z"^^xsd:dateTimeStamp .

ex:SubBatch_FB001a   a food:Batch ;
                     prov:wasDerivedFrom        ex:Batch_FB001 ;
                     prov:wasGeneratedBy        ex:Split_001 ;
                     dmfo:hasIdentifier         "GTIN-04012345-LOT-2026-001-A" .

ex:KDE_002a          a food:KDE ;
                     dmfo:manifestationOf       ex:SubBatch_FB001a ;
                     dmfo:stateWasGeneratedBy   ex:CTE_Split_001 ;
                     dmfo:evidencedBy           ex:FSMARecord_002a .
```

A merge mirror exists with `dmfo:MergeSourceIdentity` and three input
sub-batches converging into one output batch.

The deliberate governance gap (one FSMA record without
`dmfo:governedBy`) lives in the full ABox and ensures ACQ-IV-04
returns ≥ 1 row.

---

## D.4 — Split pattern (abstract)

```turtle
ex:Source_A     a dmfo:TimeVaryingEntity .

ex:Split_AC     a prov:Activity, dmfo:SplitSourceIdentity ;
                prov:used  ex:Source_A .

ex:Derived_A1   a dmfo:TimeVaryingEntity ;
                prov:wasDerivedFrom  ex:Source_A ;
                prov:wasGeneratedBy  ex:Split_AC .

ex:Derived_A2   a dmfo:TimeVaryingEntity ;
                prov:wasDerivedFrom  ex:Source_A ;
                prov:wasGeneratedBy  ex:Split_AC .
```

Acyclicity of `prov:wasDerivedFrom` is enforced by SHACL
(`shapes/identity-deriv-shapes.ttl`). OWL alone cannot exclude
cycles under open-world.

## D.5 — Merge pattern (abstract)

```turtle
ex:Merge_BCD    a prov:Activity, dmfo:MergeSourceIdentity ;
                prov:used  ex:Source_B, ex:Source_C, ex:Source_D .

ex:Merged_X     a dmfo:TimeVaryingEntity ;
                prov:wasDerivedFrom  ex:Source_B, ex:Source_C, ex:Source_D ;
                prov:wasGeneratedBy  ex:Merge_BCD .
```

The `prov:wasDerivedFrom` set carries the merge fan-in; the
`prov:wasGeneratedBy` chain is single (one merge activity per output).

---

## D.6 — Strictest-applicable-obligation composition

Two regimes simultaneously apply to one situation. The "strictest"
obligation is computed by SHACL (or by SPARQL aggregation):

```turtle
ex:Sit_X            a dul:Situation ;
                    dmfo:governedBy  ex:RegimeA, ex:RegimeB .

ex:RegimeA          a dul:Description ;
                    ex:requiresClearanceWithin "PT24H"^^xsd:duration .

ex:RegimeB          a dul:Description ;
                    ex:requiresClearanceWithin "PT4H"^^xsd:duration .
```

```sparql
SELECT ?sit (MIN(?dur) AS ?strictest)
WHERE {
    ?sit  a            dul:Situation ;
          dmfo:governedBy   ?regime .
    ?regime ex:requiresClearanceWithin ?dur .
}
GROUP BY ?sit
```

The shape-level form (SHACL) instantiates this pattern with a
`sh:SPARQLConstraint` that fires when the strictest requirement is
violated by the manifestation timestamp. Full shape body in
`profiles/maritime/mar-shapes.ttl`.

---

## D.7 — Component-necessity matrix

For every DMFO module/bridge, this table records which ACQs require
it. ✓ = the ACQ becomes unanswerable when the row component is
removed (B1-style ablation, restricted to that single component).

| Component                       | ACQ-I-01 | I-02 | II-01 | II-02 | II-03 | II-04 | II-05 | II-06 | III-01 | III-02 | III-03 | III-04 | III-05 | III-06 | III-07 | III-08 | IV-01 | IV-02 | IV-03 | IV-04 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `dmfo:TimeVaryingEntity` (Identity anchor) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dmfo:Manifestation` (State anchor, A1)    |   |   | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |   | ✓ |
| **A2** `dmfo:manifestationOf`              |   | ✓ | ✓ |   |   |   |   |   | ✓ | ✓ | ✓ |   | ✓ | ✓ | ✓ | ✓ |   |   |   |   |
| **A3** `dmfo:evidencedBy`                  |   |   |   |   | ✓ |   |   | ✓ |   |   | ✓ |   |   |   |   |   | ✓ |   |   |   |
| **A4** `dmfo:governedBy`                   |   |   |   |   |   |   | ✓ |   |   | ✓ |   |   |   | ✓ |   |   |   |   |   | ✓ |
| **A5** `dmfo:stateWasGeneratedBy`          |   |   |   | ✓ |   |   |   |   | ✓ |   |   | ✓ |   |   | ✓ | ✓ |   | ✓ |   |   |
| **A6** `dmfo:situatedAt`                       |   |   |   |   |   | ✓ |   |   |   |   |   |   |   | ✓ | ✓ |   |   |   |   |   |
| Identity-derivation module                  |   |   |   |   |   |   |   |   |   |   |   |   | ✓ |   |   | ✓ |   |   |   |   |
| `dmfo:hasIdentifier` (datatype)             | ✓ | ✓ |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   | ✓ |   |

**Reading.** Removing the State anchor (A1) breaks 18/20 ACQs. A2 alone
breaks 10/20. The most-localised bridge is A6 (3/20). Identity-derivation
is needed only for ACQ-III-05 and ACQ-III-08, but those two are
otherwise unanswerable. Every column has at least one ✓ (no ACQ is
trivial); every row has at least two ✓ (no component is unused) —
this is the **necessity** part of "component necessity".

The matrix is regenerated as JSON by
`validation/scripts/run_all_acqs.py --component-matrix` (camera-ready
release; current matrix above is the hand-curated reference).

---

## Cross-reference

* §3.2 worked example → D.1.
* §3.3 identity-derivation → D.4 + D.5.
* §4.2 component-necessity statement → D.7.
* §4.4 profile authoring → `docs/specifications/PROFILE_AUTHORING.md`.
