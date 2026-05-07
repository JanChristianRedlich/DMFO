# Maritime ABox: DMFO ↔ B2-CCO Side-by-side

## Triple counts

| KB | Triples | Individuals |
|---|---|---|
| DMFO maritime ABox (`profiles/maritime/mar-abox.ttl`) | 115 | 35 |
| B2-CCO maritime ABox (`validation/b2-cco/abox/maritime-abox.ttl`) | 108 | 37 |
| Ratio | 0.94× | +2 individuals |

The B2-CCO ABox is roughly the same size — the extra Quality
instances introduced by the inheres-in pattern (ADR-001) are offset
by the absence of explicit OWL-Time `time:Instant` individuals
(DMFO uses one per timestamp; B2-CCO inlines `xsd:dateTime` literals
on observations / acts).

## State (Manifestation) — quality-inherence

**DMFO**:

```turtle
ex:M_Discharged_HLXU  a mar:Discharged ;
    dmfo:manifestationOf      ex:CONT_HLXU3456789 ;
    dmfo:stateWasGeneratedBy  ex:Disch_77 ;
    dmfo:evidencedBy          ex:Obs_Disch_HLXU ;
    dmfo:hasManifestationTime ex:T_Disch .
```

**B2-CCO**:

```turtle
ex:Q_HLXU_Discharged  a b2mar:DischargedLocationQuality ;
    bfo:BFO_0000197 ex:CONT_HLXU3456789 .            # inheres in

ex:Disch_77  a b2mar:VesselDischarge ;               # ⊑ cco:Act
    cco:ont00001986 ex:Q_HLXU_Discharged ;            # has output
    cco:ont00001833 ex:Agent_HHLA_K12 ;               # has agent
    cco:ont00001918 ex:Berth_HHLA_CTA_03 .            # occurs at

ex:Obs_Disch_HLXU  a sosa:Observation ;
    sosa:hasFeatureOfInterest ex:Q_HLXU_Discharged .
```

**Diff** — DMFO bundles four bridges (`manifestationOf`,
`stateWasGeneratedBy`, `evidencedBy`, `hasManifestationTime`) on a
single `mar:Discharged` resource. B2-CCO splits the same information
across three resources: a Quality inhering in the bearer, an Act
producing the Quality as output, and a Measurement/Observation about
the Quality. State-history traversal in B2-CCO requires a two-step
SPARQL pattern (`?q bfo:inheres in ?bearer ; a ?stateClass`) instead
of DMFO's one-step (`?m dmfo:manifestationOf ?bearer ; a ?stateClass`).

## Activity — `cco:Act` with `cco:has agent` and `cco:has output`

**DMFO**:

```turtle
ex:Disch_77  a mar:VesselDischarge ;
    prov:startedAtTime "2026-04-12T08:15:00Z"^^xsd:dateTime ;
    prov:endedAtTime   "2026-04-12T08:21:00Z"^^xsd:dateTime ;
    prov:wasAssociatedWith ex:Agent_HHLA_CraneOp_K12 .
```

**B2-CCO**:

```turtle
ex:Disch_77  a b2mar:VesselDischarge ;               # ⊑ cco:Act
    cco:ont00001833 ex:Agent_HHLA_K12 ;               # has agent
    cco:ont00001986 ex:Q_HLXU_Discharged ;            # has output
    cco:ont00001918 ex:Berth_HHLA_CTA_03 .            # occurs at
```

**Diff** — Process start/end times: DMFO uses PROV-O datatype
properties; B2-CCO would need a `bfo:Temporal Region` with
`bfo:occupies temporal region`. For the maritime ABox we omit the
explicit temporal annotation (it does not affect any of the 20 ACQs).
Domain narrowing of the agent property is forbidden by F3, so the
`b2mar:CraneOperator` subclass is dropped; we use `cco:Agent`
directly.

## Context — `cco:Process Regulation` `prescribes` an `cco:Act`

**DMFO**:

```turtle
ex:Situation_CustodyHHLA_HLXU  a mar:CustodyTransferSituation ;
    dul:includesObject  ex:M_InYard_HLXU ;
    dul:includesObject  ex:M_Discharged_HLXU ;
    dmfo:governedBy     ex:Regime_ISPS ;
    dmfo:inZone         ex:ISPSZone_CTA .
```

**B2-CCO** (ADR-004):

```turtle
ex:CustodyTransfer_HLXU  a b2mar:CustodyTransfer_Act ;
    bfo:BFO_0000171 ex:ISPSZone_CTA .                # located in

ex:Regime_ISPS  a b2mar:RegulatoryRegime ;
    cco:ont00001942 ex:CustodyTransfer_HLXU .        # prescribes
```

**Diff** — DMFO's `dul:Situation` reifies the contextual fact and
links to multiple State manifestations via `dul:includesObject`.
B2-CCO has no `Situation` class; the act *is* the situation, and the
multiple-state inclusion is lost — the act has a single bearer
(implicit through `has output`), not a set of state manifestations.
The directionality of the regime link is reversed (regime
*prescribes* act, not act *governedBy* regime).

## Evidence — SOSA co-import (variant a)

**DMFO**:

```turtle
ex:Obs_GateRead_HLXU  a mar:Observation_GateRead ;
    sosa:resultTime         "2026-04-12T14:42:30Z"^^xsd:dateTime ;
    sosa:phenomenonTime     "2026-04-12T14:42:30Z"^^xsd:dateTime ;
    sosa:hasFeatureOfInterest ex:M_GateOut_HLXU ;
    sosa:madeBySensor        ex:Sensor_OCR_GateSouth .
```

**B2-CCO** (variant a, retains SOSA properties):

```turtle
ex:Obs_GateRead_HLXU  a sosa:Observation ;
    sosa:hasFeatureOfInterest ex:Q_HLXU_GateOut ;     # → Quality, not Manifestation
    sosa:resultTime "2026-04-12T14:42:30Z"^^xsd:dateTime ;
    sosa:phenomenonTime "2026-04-12T14:42:30Z"^^xsd:dateTime ;
    sosa:madeBySensor ex:Sensor_OCR_GateSouth .
```

**Diff** — Only the FoI target changes (Quality vs. Manifestation).
The bitemporal annotation is preserved natively. ADR-003a is the
SOSA-co-import variant; the parallel variant-b `cco:Measurement ICE`
is also emitted in the same ABox for cross-comparison.

## What is not modelled in B2-CCO

* **Multi-regime situation inclusion**. DMFO's
  `Situation_Customs_HLXU` includes one Manifestation governed by
  EU UCC; B2-CCO's reified `CustomsControl_HLXU` act is prescribed
  by exactly one regulation. To express "the same situation under
  multiple regimes", B2-CCO would need multiple regulation tokens
  prescribing the same act (allowed) but loses DMFO's "one
  Situation, multiple Descriptions" abstraction.
* **Manifestation chains via `dul:precedes` / `dul:hasFollowing`**.
  DMFO does not use these in the maritime profile, so no
  reproduction is needed.
* **OWL-Time interval anchoring**. DMFO uses `dmfo:hasManifestationTime`
  pointing at a `time:Instant`; B2-CCO uses inline xsd:dateTime
  literals on the observation/act. ACQ-II-01 (state history) compensates
  via the act's `cco:occurs at` site (proxy for spatial-temporal
  ordering) plus the observation's `sosa:resultTime`.
