# ADR-006: Identity-derivation via Act-mediated input/output chains

**Status:** accepted
**Date:** 2026-05-03
**DMFO slot affected:** Identity (transformation-induced derivation)

## Context

DMFO's identity-derivation pattern (Paper §3.3) uses
`prov:wasDerivedFrom` (transitive chain in PROV-O) plus
`dmfo:SplitSourceIdentity` / `dmfo:MergeSourceIdentity` marker classes
to model transformation-intensive contexts where entity identity is
*not* preserved across processing steps:

* **Splitting:** source α → successors β₁, …, βₙ via activity τ.
  Each βᵢ carries `prov:wasDerivedFrom α` and `prov:wasGeneratedBy τ`.
* **Merging:** sources α₁, …, αₙ → successor β via τ. β carries
  `prov:wasDerivedFrom αᵢ` for each input.
* **Transitive chains** (FSMA-204 KDE/CTE traversal): retrieved via
  `prov:wasDerivedFrom+`.

CCO 2.0 has **no PROV-O integration** and **no direct
successor-to-source derivation property**. ADR-001 + ADR-002 had
classified ACQ-III-05 and ACQ-III-08 as **(d) not meaningfully
translatable** under maritime, where the question of derivation does
not arise. The food profile (Instantiation II) re-opens the question:
splitting and merging are first-class operations, and a CCO-faithful
implementation must commit to a pattern.

## Options considered

- **Option A** — Act-mediated input/output chains.
  A successor β is "derived from" a source α iff there exists an
  intermediate `cco:Act` τ such that
  `τ cco:has input α` and `τ cco:has output β`. Transitive chains
  are SPARQL property paths of the form
  `(^cco:has_output / cco:has_input)+`. The act τ carries the
  provenance: who performed the transformation, when, where.
- **Option B** — A profile-defined fresh "wasDerivedFrom" property.
  Faithful-Translation-Rule **F3 forbids** this — it would be a
  DMFO bridge in CCO clothing.
- **Option C** — Co-import PROV-O alongside CCO (parallel to ADR-003a
  for SOSA). Would re-introduce DMFO's derivation property. Rejected
  for the same reason ADR-002 rejected this option for activities.
- **Option D** — Document derivation as a complete absence (the
  position taken under maritime in v1 of the slot-mapping). Rejected
  for food, because Splitting / Merging are explicit `cco:Act`
  operations: pretending they cannot be expressed in CCO would be a
  misrepresentation of the framework's actual capability.

## Decision

**Option A** — derivation chains are **mediated by Act tokens**.

For the food profile we add three CCO-conformant marker subclasses:

* `b2food:SplittingActivity ⊑ cco:Act` (an act with ≥ 2 distinct
  outputs from one input)
* `b2food:MergingActivity ⊑ cco:Act` (an act with ≥ 2 distinct
  inputs and one output)
* `b2food:TraceabilityLot ⊑ bfo:object` (the lot bearer; named for
  parallelism with FSMA-204 vocabulary)

Direct queries use the two-hop join:

```sparql
SELECT ?successor ?source ?transformation
WHERE {
  ?transformation a b2food:SplittingActivity ;
                  cco:has_input ?source ;
                  cco:has_output ?successor .
}
```

Transitive chains use a SPARQL 1.1 property path that hops between
acts and lots:

```sparql
SELECT ?finalLot ?sourceLot
WHERE {
  ?finalLot (^cco:has_output / cco:has_input)+ ?sourceLot .
}
```

## CCO source

- Jensen et al. (2024), *The Common Core Ontologies*, §4 *Event
  Ontology*. Acts have `cco:has input` (`ont00001921`) and
  `cco:has output` (`ont00001986`); both are sub-properties of
  `bfo:has participant` (BFO_0000057). Manufacturing, splitting, and
  combining processes are explicitly discussed as acts that transform
  inputs into outputs.
- *Modeling with the Common Core Ontologies 2024*, Chapter 4
  (Events): the act-mediated transformation is the canonical CCO
  pattern for derivation.
- IRIs:
  - `https://www.commoncoreontologies.org/ont00001921` (has input)
  - `https://www.commoncoreontologies.org/ont00001986` (has output)
  - `https://www.commoncoreontologies.org/ont00000005` (Act)

## Consequence

* **Re-classifies ACQ-III-05** from (d) to **(b)** translatable with
  modelling rework. The two-hop join works; verbose but faithful.
* **Re-classifies ACQ-III-08** from (d) to **(b)** with a
  property-path query that hops through act tokens. The chain is
  longer (each derivation step requires an act) but expressible.
* **Cost vs. DMFO**: DMFO's `prov:wasDerivedFrom+` is a single
  property path on a single property. B2-CCO's chain alternates
  inverse-`has_output` and `has_input` over Act mediation —
  **2× the query length and ~3× the path-traversal cost** in the
  ABox. ACQs III-05 and III-08 thus survive on B2-CCO, but at
  measurable performance and readability expense (reported in
  `results/b2-cco-perf.json`).
* **Honest comparison**: the DMFO advantage on identity-derivation
  is therefore **not categorical (B2-CCO can express it) but
  ergonomic (DMFO needs ½ the query length)**. The manuscript should
  acknowledge this rather than treat it as a "B2-CCO can't" claim.

## SPARQL/Turtle illustration

ABox fragment (one split + one merge):

```turtle
ex:Lot_RAW_NOR  a b2food:TraceabilityLot ;
    rdfs:label "Raw lot NOR-2026-0312"@en .

ex:Activity_Split_τ1  a b2food:SplittingActivity ;
    cco:ont00001921 ex:Lot_RAW_NOR ;            # has input
    cco:ont00001986 ex:Lot_PROC_A ;             # has output
    cco:ont00001986 ex:Lot_PROC_B .             # has output (second)

ex:Lot_PROC_A  a b2food:TraceabilityLot .
ex:Lot_PROC_B  a b2food:TraceabilityLot .
```

Direct successor-to-source query:

```sparql
SELECT ?successor ?source ?act
WHERE {
  ?act a b2food:SplittingActivity ;
       cco:ont00001921 ?source ;     # has input
       cco:ont00001986 ?successor .
}
```

Transitive ancestor query (FSMA-204 chain):

```sparql
SELECT ?finalLot ?sourceLot
WHERE {
  ?finalLot (^cco:ont00001986 / cco:ont00001921)+ ?sourceLot .
  # ^has_output then has_input, repeated; hops through Act tokens.
}
```

## Reading guide for the manuscript

The B2-CCO food score *with ADR-006* answers ACQ-III-05 and
ACQ-III-08 — earlier reported as (d) under maritime. The
re-classification is **not** post-hoc tuning: ADR-006 is a documented
standard CCO pattern that simply was not exercised by maritime data.
This is exactly the case Faithful-Translation-Rule F1 anticipates:
"if a slot has no native CCO pendant, the modelling falls back to a
documented absence" — but the slot *does* have a pendant for food
(act-mediated derivation), so the absence does not apply.

The cost is measured in query length and traversal performance, not
in answerability. Section 4.2 of the manuscript should report the
food B2-CCO score and the ergonomic differential explicitly.
