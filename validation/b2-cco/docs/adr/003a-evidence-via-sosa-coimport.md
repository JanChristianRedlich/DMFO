# ADR-003a: Evidence via isolated SOSA co-import

**Status:** accepted (variant a)
**Date:** 2026-05-03
**DMFO slot affected:** Evidence

## Context

DMFO uses `sosa:Observation` as the Evidence anchor and links a
manifestation to its observation via `dmfo:evidencedBy ⊑ inverse(
sosa:hasFeatureOfInterest)` (A3). CCO does not co-import SOSA in
its standard distribution.

The Evidence slot has no native CCO pendant (slot-mapping documented
absence). Two implementation variants are evaluated to surface this
gap:

* **(a)** isolated SOSA co-import — this ADR.
* **(b)** CCO-native Measurement-ICE pattern — see ADR-003b.

## Options considered (within variant a)

- **Option A** — Co-import SOSA at version 2017-10 alongside CCO 2.0,
  use SOSA's classes natively (`sosa:Observation`, `sosa:Sensor`,
  `sosa:hasFeatureOfInterest`). Quality is the
  `sosa:hasFeatureOfInterest`. **No** typed sub-property of
  `sosa:hasFeatureOfInterest` is introduced (would violate
  Faithful-Translation-Rule F3).
- **Option B** — Co-import SOSA but redirect feature-of-interest at
  the bearer (the container) rather than at the quality. Loses the
  "evidence grounds the manifestation" semantics.

## Decision

**Option A**. The observation's `sosa:hasFeatureOfInterest` points to
the `bfo:Quality` instance modelled in ADR-001, not at the bearer.
This preserves the DMFO semantics of "evidence grounds the state of
the bearer at a time" without inventing a typed bridge.

## CCO source

- Jensen et al. (2024) does **not** integrate SOSA.
- CCO 2.0 release notes acknowledge SOSA/SSN as a peer vocabulary
  outside the CCO suite.
- This variant is therefore an **isolated co-import for evaluation
  only**, documented as out-of-scope for permanent CCO integration
  per Faithful-Translation-Rule F1.

## Consequence

* **Enables** ACQ-II-03 (state→evidence), ACQ-III-03
  (state→evidence→sensor) via the SOSA path.
* **Acknowledged drawback**: this variant *is* a partial reproduction
  of DMFO (A3) without the typed sub-property. It demonstrates that
  to reach DMFO answerability, even the SOSA-coimport baseline must
  use the same SOSA properties DMFO uses.
* **Honest comparison**: the per-ACQ score difference between
  variant (a) and DMFO measures the cost of *not having the typed
  inverse sub-property*. It is small (≤ 1 ACQ) — variant (a)
  reaches most evidence ACQs.

## SPARQL/Turtle illustration

```turtle
@prefix sosa: <http://www.w3.org/ns/sosa/> .
ex:Obs_GateRead_HLXU  a sosa:Observation ;
    sosa:hasFeatureOfInterest ex:CONT_GateOutLocationQuality ;
    sosa:resultTime "2026-04-12T14:42:30Z"^^xsd:dateTime ;
    sosa:madeBySensor ex:Sensor_OCR_GateSouth .
```

Evidence-grounded query:

```sparql
SELECT ?observation ?sensor WHERE {
  ?q bfo:BFO_0000197 ex:CONT_HLXU3456789 .       # inheres in
  ?observation sosa:hasFeatureOfInterest ?q ;
               sosa:madeBySensor ?sensor .
}
```
