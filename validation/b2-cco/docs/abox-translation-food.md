# Food ABox: DMFO ↔ B2-CCO Side-by-side

## Triple counts

| KB | Triples |
|---|---|
| DMFO food ABox (`profiles/food/food-abox.ttl`) | 102 |
| B2-CCO food ABox (`validation/b2-cco/abox/food-abox.ttl`) | 105 |
| Ratio | 1.03× |

The food ABox stays roughly the same size despite the more complex
identity-derivation pattern (ADR-006). The Act-mediation overhead is
offset by the disappearance of OWL-Time `time:Instant` individuals
and DMFO-specific `dmfo:SplitSourceIdentity` typing.

## Identity-derivation (split + merge) — ADR-006

**DMFO (PROV-O wasDerivedFrom + Split/MergeSourceIdentity marker):**

```turtle
ex:Lot_RAW_NOR_2026_0312  a food:RawIngredientLot , dmfo:SplitSourceIdentity .

ex:Lot_PROC_A_2026_0413   a food:ProcessedLot ;
    prov:wasDerivedFrom   ex:Lot_RAW_NOR_2026_0312 ;
    prov:wasGeneratedBy   ex:Activity_Split_τ1 .

ex:Lot_PROC_B_2026_0413   a food:ProcessedLot ;
    prov:wasDerivedFrom   ex:Lot_RAW_NOR_2026_0312 ;
    prov:wasGeneratedBy   ex:Activity_Split_τ1 .
```

**B2-CCO (Act-mediated input/output, ADR-006):**

```turtle
ex:Lot_RAW_NOR_2026_0312  a b2food:RawIngredientLot .

ex:Activity_Split_τ1  a b2food:SplittingActivity ;
    cco:ont00001921 ex:Lot_RAW_NOR_2026_0312 ;          # has input
    cco:ont00001986 ex:Lot_PROC_A_2026_0413 ,           # has output (lot 1)
                    ex:Lot_PROC_B_2026_0413 ,           # has output (lot 2)
                    ex:Q_PROC_A_InProduction ,          # has output (state of lot 1)
                    ex:Q_PROC_B_InColdStorage .         # has output (state of lot 2)
```

**Diff** — DMFO encodes derivation as a *direct property between lots*
(`prov:wasDerivedFrom`); B2-CCO encodes it as *act mediation* through
`cco:has_input` and `cco:has_output`. The B2-CCO query for the
derivation chain is therefore a two-hop pattern:

```sparql
?act cco:has_input  ?source ;
     cco:has_output ?successor .
```

vs. DMFO's single-hop:

```sparql
?successor prov:wasDerivedFrom ?source .
```

For transitive chains (FSMA-204 KDE/CTE traversal, ACQ-III-08), DMFO
uses the SPARQL property path `prov:wasDerivedFrom+` (one path
expression on one property). B2-CCO uses the alternating-hop property
path `(^cco:has_output / cco:has_input)+` — twice as many tokens but
still expressible (Paper §4.2 reports this as **ergonomic cost, not
expressivity loss**).

## Splitting + merging activity outputs

In the consolidated B2-CCO food ABox, each transformation activity
brings into being **both** the new lot bearer **and** the lot's
initial state quality. This is faithful BFO/CCO modelling: the act
produces all entities that come into existence through it. The
alternative — splitting the production of the lot from the production
of its initial quality across two acts — is also CCO-conformant but
makes ACQ-III-01 (state→activity→agent) require a join through
`bfo:has_temporal_part` between the two acts. We adopt the
consolidated form to keep the maritime and food profiles structurally
parallel and the ACQ catalogue uniformly translatable.

## Deliberate gaps for Class IV ACQs

| ACQ | DMFO gap | B2-CCO gap |
|---|---|---|
| ACQ-IV-01 (evidence gap) | `M_InColdStorage_PROC_B` has no `dmfo:evidencedBy` | `Q_PROC_B_InColdStorage` has no `sosa:hasFeatureOfInterest`-pointing observation |
| ACQ-IV-02 (causal gap) | `M_InColdStorage_OrphanReceipt` has no `dmfo:stateWasGeneratedBy` | `Q_RAW_ING_OrphanColdStorage` has no act with `cco:has_output` pointing at it |
| ACQ-IV-03 (id-scheme gap) | TVE has identifier but no `dmfo:identifierScheme` | (semantically shifted: object with no designating ICE — see ADR-001) |
| ACQ-IV-04 (governance gap) | `Situation_PendingRegime_OrphanReceipt` has no `dmfo:governedBy` | `Pending_OrphanReceipt` act not prescribed by any regulation |

ACQ-IV-03 is the only one where the deliberate gap *cannot* be
mirrored 1:1 — see ADR-001's "scheme is encoded in ICE class, not
as a separate property" note.

## What is not modelled

* **`dmfo:Split/MergeSourceIdentity` marker classes** — replaced by
  the typing of the *activity* (`b2food:SplittingActivity`,
  `b2food:MergingActivity`). The lot itself carries no
  derivation-role marker.
* **`dmfo:hasManifestationTime` time-instant anchoring** — replaced
  by inline `xsd:dateTime` on observations and acts.
* **DUL multi-regime situation inclusion** — same limitation as
  maritime profile (ADR-004).
