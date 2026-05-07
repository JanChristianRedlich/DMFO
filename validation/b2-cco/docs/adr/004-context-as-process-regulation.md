# ADR-004: Context slot via cco:Process Regulation

**Status:** accepted
**Date:** 2026-05-03
**DMFO slot affected:** Context

## Context

DMFO uses `dul:Situation` and `dul:Description` for the Context slot,
linked by `dmfo:governedBy : Situation → Description` (A4). The DnS
"Situation reified as truth-maker for a Description" pattern is a
DOLCE-Ultralite commitment that has no direct CCO equivalent.

CCO has `cco:Process Regulation` (`ont00001324`, formerly *Action
Regulation*) — a subclass of `cco:Prescriptive Information Content
Entity` (`ont00000965`, formerly *Directive Information Content
Entity*) that "prescribes" a process or class of processes. There
is no CCO `Situation` class.

## Options considered

- **Option A** — Reify situation as `cco:Act` (the act that the
  regulation governs *is* the situation). Use `cco:prescribes`
  (`ont00001942`) as the regulation→act link.
- **Option B** — Reify situation as a `cco:Information Content
  Entity` describing the relevant facts (a "case file"). Use
  `cco:describes` (`ont00001982`) for the link.
- **Option C** — Co-import DUL+DnS into CCO. Would parallel ADR-003a
  but reintroduce a competing upper-level. Rejected: contradicts the
  premise of a CCO-native baseline.

## Decision

**Option A**. The situation *is* the act. A custody-transfer
situation is encoded as a `cco:Act` token (subclass
`b2mar:CustodyTransfer_Act`) that the relevant
`cco:Process Regulation` instance prescribes.

The directionality differs from DMFO: where DMFO has
`Situation → governedBy → Description`, CCO has
`Regulation → prescribes → Act`. Queries must reflect this.

## CCO source

- Jensen et al. (2024), §5 *Information Entity Ontology* — Process
  Regulation as the canonical class for normative directives.
- "Modeling with CCO 2024", Chapter 5 (Information Content Entities).
- CCO opaque IRIs:
  - `https://www.commoncoreontologies.org/ont00001324` (Process
    Regulation)
  - `https://www.commoncoreontologies.org/ont00000965` (Prescriptive
    ICE)
  - `https://www.commoncoreontologies.org/ont00001942` (prescribes)

## Consequence

* **Enables** ACQ-II-05 (situation→regime) with reversed direction:
  `?regulation cco:prescribes ?act`.
* **Blocks** the *multi-regime* semantics natural to DnS: in DnS one
  Situation can be `governedBy` multiple Descriptions, all evaluated
  against the same situation. In CCO, a single act is prescribed by
  exactly one regulation token; multiple regimes require multiple
  prescribes-relations or multiple regulation tokens, with no
  natural notion of *the same situation under different regimes*.
  ACQ-III-02 (state→situation→regime) under multi-regime data is
  partially answerable (returns one row per regulation, but lacks
  the "same situation" anchor).
* **Cost**: each contextual situation requires a class-level
  `b2mar:Act` subclass + the regulation. DMFO uses one
  `dul:Situation` instance + one `dul:Description` per regime.

## SPARQL/Turtle illustration

```turtle
ex:CustodyTransfer_HLXU  a b2mar:CustodyTransfer_Act ;
    cco:ont00001833 ex:Agent_HHLA_K12 .          # has agent
ex:Regime_ISPS  a b2mar:RegulatoryRegime ;       # ⊑ Process Regulation
    cco:ont00001942 ex:CustodyTransfer_HLXU .    # prescribes
```

Situation→regime query (reversed direction vs. DMFO):

```sparql
SELECT ?act ?regulation WHERE {
  ?regulation a b2mar:RegulatoryRegime ;
              cco:ont00001942 ?act .             # prescribes
}
```
