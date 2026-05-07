# SOSA × CCO Integration

This document explains how the B2-CCO baseline integrates SOSA/SSN
in the `sosa-coimport` variant (ADR-003a) and why the
`strict-native` variant (ADR-003b) drops SOSA entirely. The specific
question addressed: how is the duplication between
`cco:Measurement Process` / `cco:Measurement ICE` and
`sosa:Observation` resolved, and which property bridge is used?

---

## The duplication

CCO 2.0 carries a **measurement** pattern:

* `cco:Measurement Process` — the act of measuring (a `bfo:Process`
  sub-class).
* `cco:Measurement ICE` — the Information Content Entity that carries
  the measured value (sub-class of `cco:Information Content Entity`).
* `cco:is_about` — links the ICE to the entity being measured.
* `cco:has_proper_part` / `bfo:has_continuant_part` — links the
  `cco:Quality` (e.g. temperature) to the bearer.

SOSA carries a **partly overlapping** observation pattern:

* `sosa:Observation` — the act of observing.
* `sosa:hasFeatureOfInterest` — links observation to the entity being
  observed.
* `sosa:observedProperty` — the property that is the focus of the
  observation.
* `sosa:hasResult` — the carrier of the result value.
* `sosa:madeBySensor` — the device that produced the observation.

The overlap is non-trivial:

| SOSA construct | CCO equivalent | Diagnosis |
|---|---|---|
| `sosa:Observation` | `cco:Measurement Process` | Both denote the act; CCO uses BFO Process subclass, SOSA uses a SOSA-specific class. |
| `sosa:hasFeatureOfInterest` | `cco:is_about` (on the ICE) | One step apart: SOSA links from observation to FoI directly; CCO routes through the ICE. |
| `sosa:hasResult` | `cco:Measurement ICE` itself | CCO conflates "the value" with "the ICE that bears the value". |
| `sosa:madeBySensor` | (no direct CCO concept) | CCO has no `cco:Sensor` class. The closest is `cco:Measurement Process Configuration` which is not a device class. |
| `sosa:observedProperty` | `bfo:Quality` (the property the ICE is_about) | SOSA names the property; CCO names the quality. Off by one level of indirection. |

---

## ADR-003a (sosa-coimport variant) — the "co-import" resolution

In the **sosa-coimport** variant the B2-CCO base ontology is
extended by `b2-cco-base-sosa.ttl`, which imports SOSA *as-is* and
declares two **alignment statements**:

```turtle
sosa:Observation
    rdfs:subClassOf cco:Measurement_Process .

cco:is_about
    rdfs:subPropertyOf [ owl:inverseOf sosa:hasFeatureOfInterest ] .
```

That is the **only** pair of axioms that bridges the two
vocabularies. There is **no** typed B2-CCO bridge property
(F3 prohibition). The integration happens at the import level and
relies on:

1. SOSA's permissiveness — `sosa:Observation` does not commit to
   "discrete event" vs. "continuous process", which would otherwise
   collide with `cco:Measurement_Process` being a `bfo:Process`.
2. The fact that `cco:is_about` and `sosa:hasFeatureOfInterest`
   are inverses up to the ICE level of indirection. This is why
   the second axiom is `sub-property-of inverse-of` rather than
   `equivalent-property`.

Where SOSA carries information CCO cannot carry natively
(`sosa:madeBySensor`, `sosa:observedProperty` as a property name
rather than an object identity), the SOSA assertions are kept
*alongside* the CCO ones. Queries that need them target the SOSA
predicate (e.g. `sosa:madeBySensor`); queries that need the CCO
ICE-level information target `cco:is_about`.

This is what makes ACQ-III-03 ("which sensor produced the
observation that evidences this state?") answerable in the
sosa-coimport variant: the SPARQL query traverses
`?obs sosa:madeBySensor ?sensor` directly. Without the SOSA
co-import (i.e. in the strict-native variant) there is no sensor
concept in CCO, and ACQ-III-03 becomes structurally underdetermined
— classified `(d)` per ADR-003b.

---

## ADR-003b (strict-native variant) — the "drop SOSA" resolution

The strict-native variant drops `b2-cco-base-sosa.ttl` and uses
**only** CCO. The four ACQs that depended on SOSA constructs are
re-classified:

| ACQ | sosa-coimport | strict-native | Reason |
|---|---|---|---|
| ACQ-II-03 | ✓ (a — pure SOSA) | ✓ (b — CCO `cco:is_about`) | Both routes work; native is one step longer. |
| ACQ-II-06 | ✓ (a — `sosa:observedProperty`) | ✗ (d — no observed-property in CCO) | The SOSA "what was observed" question has no CCO native form. |
| ACQ-III-03 | ✓ (a — `sosa:madeBySensor`) | ✗ (d — no sensor concept in CCO) | CCO has no device class. |
| ACQ-IV-01 | ✓ (a — `FILTER NOT EXISTS sosa:hasFeatureOfInterest`) | ✗ (d — same reason as ACQ-II-06; the negation has no CCO form either) | The absence-detection mirror of II-06. |

---

## Why this matters for the paper

The paper's claim — that B2-CCO's coverage gap is **systematic**, not
**stylistic** — relies on the fact that the four ACQ-class shifts are
attributable to a *single* CCO commitment (no native sensor / no
native observed-property concept). Adding SOSA fixes them. Adding
typed bridges (the DMFO move) fixes them more cleanly *and* fixes
ACQ-III-04 + ACQ-IV-03, which the SOSA co-import does **not** fix.

This is the architectural difference, expressed as a 3-row table:

| Variant                   | ACQs answered (sosa) | + ACQs gained vs. native | + ACQs gained vs. DMFO |
|---|---|---|---|
| Strict-native CCO          | 15 / 20 | (baseline)            | DMFO is +5         |
| sosa co-import             | 17 / 20 | +2 (II-06, III-03 — the SOSA-specific four shrink to two; IV-01 also recovers) | DMFO is +3         |
| DMFO + (A1)–(A6)           | 20 / 20 | +5 vs. native, +3 vs. sosa | (top)            |

The two ACQs that DMFO answers but sosa-coimport does not are
ACQ-III-04 (PROV-O qualified usage / hadRole — ADR-002) and
ACQ-IV-03 (typed scheme identifier — ADR-007). These are
**not** SOSA-related, so SOSA co-import doesn't help.

---

## Pointer

* ADR-003a: [`adr/003a-evidence-via-sosa-coimport.md`](adr/003a-evidence-via-sosa-coimport.md)
* ADR-003b: [`adr/003b-evidence-via-measurement-ice.md`](adr/003b-evidence-via-measurement-ice.md)
* The two TBox files that differ: `validation/b2-cco/ontology/b2-cco-base.ttl`
  (always loaded) and `validation/b2-cco/ontology/b2-cco-base-sosa.ttl`
  (only loaded in the sosa-coimport variant).
* Variant switch in the runner:
  `bash validation/scripts/b2cco-run-acqs.sh` (default) vs.
  `VARIANT=native bash validation/scripts/b2cco-run-acqs.sh`.
