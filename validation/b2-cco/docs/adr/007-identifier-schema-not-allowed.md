# ADR-007: Identifier-Schema property — not introduced (F3-prohibited)

**Status:** accepted
**Date:** 2026-05-06
**DMFO slot affected:** Identity (cross-cutting)
**ACQs affected:** ACQ-IV-03 (FAIR F1 — identifier-scheme-gap)

## Context

DMFO commits to `dmfo:hasIdentifier` as a datatype property on
`dmfo:TimeVaryingEntity` (Identity slot, paper §3.2 / Listing 1).
Where multiple identifier schemes coexist (GS1 SGTIN, GS1 SSCC, IATA
ULD, EPCIS instance-id, etc.), DMFO additionally allows a profile to
introduce a typed datatype property *per scheme* to make
ACQ-IV-03 ("which entities lack an identifier under scheme S?")
expressible as a `FILTER NOT EXISTS` over a *typed* predicate.

CCO 2.0 carries the corresponding pattern via the
**Information Content Entity (ICE) about Identifier** construction:
an `cco:Identifier ICE` is the carrier of the identifier value, and
`cco:is_about` links the ICE to the entity. There is **no** native
CCO predicate of the form `b2cco:hasIdentifierScheme` or
`b2cco:hasGS1SGTIN` — and per **F3 of the Faithful-Translation-Rule**,
B2-CCO must not introduce one.

## Decision

B2-CCO does **not** introduce a typed identifier-scheme datatype
property. ACQ-IV-03 is answered (or fails to be answered) by:

1. Asking the question in **CCO-native form**:
   ```sparql
   SELECT ?tve WHERE {
       ?tve a ?T .
       ?T rdfs:subClassOf* cco:Continuant_Mereological_Entity .
       FILTER NOT EXISTS {
           ?ice  cco:is_about     ?tve ;
                 a                cco:IdentifierICE .
       }
   }
   ```
2. Documenting the resulting **scheme-shift gap**: the CCO answer is
   a *list of entities without any ICE-identifier*, **not** a list of
   entities without an identifier *under a given scheme S*. The
   semantic shift is recorded in
   [`../acq-translation.md`](../acq-translation.md) under ACQ-IV-03
   with classification `(c)` (semantically shifted) per the strict
   rubric of Paper §4.2.

## Consequences

* ACQ-IV-03 is **not natively answerable** in B2-CCO under the strict
  rubric. The CCO query returns a list, but the list is over the
  wrong granularity (any-scheme vs. given-scheme).
* This is a *systematic* CCO limitation, not a B2-CCO modelling
  shortcut. Adding `b2cco:hasGS1SGTIN` would violate F3 ("no DMFO
  bridge in CCO clothing"). The same prohibition applies to any
  scheme-typed object property whose only purpose is to make
  scheme-level absence detection possible.
* DMFO retains the capability **because** it allows profile-level
  datatype properties to carry scheme information (`mar:gs1Sgtin`,
  `food:gtinPlusBatch`, etc.), and the ACQ binds against the typed
  scheme predicate.

## Considered alternatives

1. **`b2cco:hasGS1SGTIN` typed datatype property in `b2-cco-base.ttl`.**
   Rejected — violates F3 (typed predicate whose intended semantics
   is "DMFO scheme-typed identifier in CCO clothing"). Would also
   require one such property per scheme, multiplying F3 violations
   per ACQ.
2. **Sub-classing `cco:IdentifierICE` per scheme** (e.g.
   `cco:IdentifierICE → b2cco:GS1SGTINIdentifierICE`).
   Rejected — F3 still bites: a sub-class introduced solely to host
   scheme-level NOT EXISTS is a typed bridge in disguise.
   Additionally, CCO's user guide does not document such a pattern.
3. **Reusing `cco:designates` with a custom Annotation Property
   `b2cco:scheme`.** Considered. The Annotation Property does not
   create a logical commitment, so F3 is technically not violated.
   But the resulting `FILTER NOT EXISTS` query is fragile: an
   `rdfs:label` rewrite or a synonym break the negation. Rejected
   on robustness grounds.
4. **Recording the gap and classifying ACQ-IV-03 as `(c)` /
   semantically shifted.** **Accepted.** This is consistent with
   F5 ("diagnosis over patching") and with the per-ACQ status
   reported in `validation/results/comparison-dmfo-vs-b2cco-*.csv`.

## Citation

* Smith et al. (2024). *The Common Core Ontologies* — FOIS 2024,
  §4.3 "Information Content Entities".
* CCO 2.0 user guide, "Modeling with the Common Core Ontologies",
  Pattern 7 (Identifiers).
* Wilkinson et al. (2016). *FAIR Guiding Principles*, principle F1
  ("(meta)data are assigned a globally unique and persistent
  identifier").

## Compliance check

```
# Faithful-Translation-Rule: F1 (CCO ICE pattern), F3 (no typed scheme
# property), F4 (this ADR), F5 (diagnosis recorded).
```
