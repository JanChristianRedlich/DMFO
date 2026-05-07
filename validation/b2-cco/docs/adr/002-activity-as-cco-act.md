# ADR-002: Activity slot via cco:Act + cco:Agent

**Status:** accepted
**Date:** 2026-05-03
**DMFO slot affected:** Activity

## Context

DMFO uses `prov:Activity` as the Activity anchor and `prov:Agent` as
the agent anchor, with `dmfo:stateWasGeneratedBy` (A5) as a typed
sub-property of `prov:wasGeneratedBy` linking `dmfo:Manifestation` to
`prov:Activity`. CCO does not co-import PROV-O.

## Options considered

- **Option A** — `cco:Act` (`ont00000005`): an intentional process
  performed by an agent. Subclass of `bfo:process`. Pairs with
  `cco:Agent` (`ont00001017`) via `cco:has agent` (`ont00001833`).
- **Option B** — `bfo:process` directly: covers non-intentional
  processes too (e.g. erosion, diffusion). No agent commitment.
- **Option C** — Co-import PROV-O with no integration. Would
  reintroduce `prov:Activity` and recreate DMFO's bridge architecture
  surreptitiously (violates Faithful-Translation-Rule F3).

## Decision

**Option A** (`cco:Act`) for agent-bearing maritime operations
(crane transfers, vessel discharges, gate movements). Where a
non-intentional process occurs (e.g. drift, evaporation in a future
food extension), fall back to **Option B** (`bfo:process`) with no
agent attribution.

The DMFO `dmfo:stateWasGeneratedBy` link is reproduced as
`cco:has output` (`ont00001986`) from the `cco:Act` token to the
`bfo:Quality` produced by the act, **with no domain/range narrowing**
beyond what CCO already declares (Faithful-Translation-Rule F3).

## CCO source

- Jensen et al. (2024), §4 *Event Ontology* — `cco:Act` is the
  intentional-process class with `cco:has agent` qualifier.
- "Modeling with CCO 2024", Chapter 4 (Events).
- CCO opaque IRIs:
  - `https://www.commoncoreontologies.org/ont00000005` (Act)
  - `https://www.commoncoreontologies.org/ont00001017` (Agent)
  - `https://www.commoncoreontologies.org/ont00001833` (has agent)
  - `https://www.commoncoreontologies.org/ont00001986` (has output)
  - `https://www.commoncoreontologies.org/ont00001921` (has input)
  - `https://www.commoncoreontologies.org/ont00001918` (occurs at)

## Consequence

* **Enables** ACQ-II-02 (state→activity), ACQ-III-01
  (state→activity→agent) via the `cco:has output` / `cco:has agent`
  chain.
* **Cost** vs. DMFO: each State → Activity link traverses `bfo:Quality`
  rather than `dmfo:Manifestation`, so the SPARQL has an extra hop:
  `?q bfo:inheres in ?bearer .  ?act cco:has output ?q .`
* **Cost** vs. PROV-O: no `prov:wasInformedBy` analogue for causal
  antecedents between activities — CCO has `bfo:precedes` for
  temporal ordering but not a typed causal-information link. Under
  the strict reading of PROV-O Rec §5.7 (qualified usage with typed
  `prov:hadRole`), ACQ-III-04 is **structurally underdetermined (d)**
  in B2-CCO: the entity-flow witness via `cco:has_input` /
  `cco:has_output` can be reconstructed, but CCO has no analogue of
  `prov:Role` and no qualifying construct over `cco:has_input` to
  expose what role the carrier plays in the dependent activity's
  plan. Adding such a role property would violate
  Faithful-Translation-Rule F3.

## SPARQL/Turtle illustration

```turtle
ex:Disch_77  a b2mar:VesselDischarge ;     # ⊑ cco:Act
    cco:ont00001833 ex:Agent_HHLA_K12 ;    # has agent
    cco:ont00001986 ex:CONT_DischargedQuality ;   # has output
    cco:ont00001918 ex:Berth_HHLA_CTA_03 . # occurs at
```
