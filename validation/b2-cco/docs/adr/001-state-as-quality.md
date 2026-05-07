# ADR-001: Identity + State via Quality-Inherence

**Status:** accepted
**Date:** 2026-05-03
**DMFO slot affected:** Identity, State

## Context

DMFO's State slot is anchored at `dmfo:Manifestation`, jointly typed
under (A1) as `prov:Entity ⊓ dul:Event ⊓ sosa:FeatureOfInterest`. It is
linked to its Identity-bearer via `dmfo:manifestationOf` (A2).

CCO has **no class corresponding to `dmfo:Manifestation`**. CCO models
state through the BFO continuant/occurrent framework: a
`bfo:Material Entity` (the bearer) carries `bfo:Quality` instances that
`bfo:inheres in` it; a `cco:Stasis of Quality` is a process-profile-of
sort that captures a quality holding stable over a temporal region.

## Options considered

- **Option A** — Quality-inherence: model each "state" as a
  `bfo:Quality` instance inhering in the bearer. State changes are
  modelled as new quality instances replacing old ones. Stable
  intervals get a `cco:Stasis of Quality` annotation.
- **Option B** — Process-profile: model the state-bearing entity's
  participation in a `bfo:Process` and use `bfo:Process Profile`
  (BFO_0000144) to pick out the relevant phase.
- **Option C** — Pure ICE: reify the state as an
  `cco:Information Content Entity` *describing* the bearer at a time
  point. The state is content, not a metaphysical entity.

## Decision

**Option A (quality-inherence)**, with optional Option B for activities
that have internal phase structure (e.g. a discharge operation has
sub-phases). Option C is rejected: encoding a state as content
inverts the BFO ontology of qualities and would undermine subsequent
process-profile reasoning.

For B2-CCO maritime: a container's "InYard" state is the quality
`b2mar:InYardLocationQuality` inhering in the container, holding
during the temporal region of the relevant `cco:Stasis of Quality`.

## CCO source

- Jensen et al. (2024), §3 *Object Ontology* and §3.2 *Quality
  Ontology* — quality-inherence is the canonical CCO pattern for
  "state of an entity at a time".
- BFO ISO/IEC 21838-2:2020 §4.2 (Quality), §4.3 (Process Profile).
- CCO opaque IRIs:
  - `https://www.commoncoreontologies.org/ont00000850` (Stasis of Quality)
  - `http://purl.obolibrary.org/obo/BFO_0000019` (Quality)
  - `http://purl.obolibrary.org/obo/BFO_0000197` (inheres in)
  - `http://purl.obolibrary.org/obo/BFO_0000144` (Process Profile)

## Consequence

* **Enables** ACQ Class I (identity-only lookup), ACQ Class II for
  state→quality traversals via `bfo:inheres in`.
* **Blocks** the joint typing of state phases as
  `prov:Entity ⊓ dul:Event ⊓ sosa:FeatureOfInterest` (DMFO A1). Any
  ACQ that traverses a path requiring this joint typing — typically
  Class III multi-bridge queries that bind the state to provenance,
  evidence, and observation simultaneously — has no CCO-native
  equivalent. See ADR-002 / ADR-003 for the State→Activity and
  State→Evidence consequences.
* **Cost**: state-history queries that DMFO answers in a single
  triple pattern (`?m dmfo:manifestationOf ?tve`) require a
  two-step traversal in B2-CCO (`?q bfo:inheres in ?tve` plus
  `?q a ?qualityClass`). Triple count grows ~1.4× for the same
  scenario.

## SPARQL/Turtle illustration

```turtle
@prefix bfo:   <http://purl.obolibrary.org/obo/> .
@prefix cco:   <https://www.commoncoreontologies.org/> .
@prefix b2mar: <https://w3id.org/dmfo/baseline/cco/maritime#> .
@prefix ex:    <https://w3id.org/dmfo/baseline/cco/example#> .

ex:CONT_HLXU3456789  a b2mar:Container .
ex:CONT_InYardQuality  a b2mar:InYardLocationQuality ;
    bfo:BFO_0000197 ex:CONT_HLXU3456789 .   # inheres in
```

State-history query:

```sparql
SELECT ?qualityClass WHERE {
  ?q bfo:BFO_0000197 ex:CONT_HLXU3456789 ;     # inheres in
     a ?qualityClass .
}
```
