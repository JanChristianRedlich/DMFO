# ADR-005: Location slot via bfo:Site + bfo:located in

**Status:** accepted
**Date:** 2026-05-03
**DMFO slot affected:** Location

## Context

DMFO uses `geo:Feature` as the Location anchor and links a contextual
situation to its institutional zone via
`dmfo:inZone ⊑ geo:sfWithin` (A6). GeoSPARQL provides
`sfWithin`/`sfIntersects`/`sfTouches` mereotopological relations.

CCO has `cco:Geospatial Region` (`ont00000472`) and
`cco:Geospatial Location` (`ont00000487`), but **no native GeoSPARQL
spatial-relation algebra**. BFO provides only `bfo:located in`
(BFO_0000171) and the mereological `bfo:has spatial part` /
`bfo:occupies spatial region` (BFO_0000210) family.

## Options considered

- **Option A** — `bfo:Site` (BFO_0000029) for institutional zones,
  `bfo:located in` for the situation→zone relation. No GeoSPARQL
  topological reasoning. No typed `inZone`-equivalent sub-property.
- **Option B** — `cco:Geospatial Region` for purely geometric
  zones, `cco:occurs at` for activities. Loses the "institutional"
  semantics of the zone (a customs-controlled zone is
  *constituted-by-decision*, not by its boundary).
- **Option C** — Co-import GeoSPARQL alongside CCO (parallel to
  ADR-003a). Rejected: ADR-005 holds the institutional-vs-geometric
  distinction more cleanly with `bfo:Site` than with GeoSPARQL.

## Decision

**Option A** with one nuance: institutional zones (ISPS, customs
control) are `bfo:Site` instances; geometric features (yard outlines,
berth coordinates) are `cco:Geospatial Region`. The
situation→institutional-zone link is `bfo:located in`.

## CCO source

- Jensen et al. (2024), §6 *Geospatial Ontology*.
- BFO ISO/IEC 21838-2:2020 §4.4 (Site).
- IRIs:
  - `http://purl.obolibrary.org/obo/BFO_0000029` (Site)
  - `http://purl.obolibrary.org/obo/BFO_0000171` (located in)
  - `https://www.commoncoreontologies.org/ont00000472` (Geospatial
    Region)
  - `https://www.commoncoreontologies.org/ont00000487` (Geospatial
    Location)

## Consequence

* **Enables** ACQ-II-04 (situation→zone) via plain `bfo:located in`.
* **Blocks** ACQ-III-06 (customs consistency over zones+regimes)
  *partially*: the query can join via `bfo:located in` but loses the
  GeoSPARQL `sfWithin` transitive-spatial-containment that DMFO
  uses to find regulated zones containing the activity zone.
* **Blocks** any spatial-topology query (sfTouches, sfOverlaps).
  Maritime ACQ catalogue does not exercise these so the cost is
  bounded; a future profile that needs spatial reasoning (e.g.
  port-area logistics) would be markedly harder under B2-CCO.

## SPARQL/Turtle illustration

```turtle
ex:Yard_CTA  a b2mar:TerminalYard .             # ⊑ bfo:Site
ex:ISPSZone_CTA  a b2mar:ISPSZone ;              # ⊑ bfo:Site
    bfo:BFO_0000171 ex:Yard_CTA .               # located in (zone within yard)
ex:CustodyTransfer_HLXU  bfo:BFO_0000171 ex:ISPSZone_CTA .
```

Situation→zone query:

```sparql
SELECT ?act ?zone WHERE {
  ?act bfo:BFO_0000171 ?zone .                  # located in
  ?zone a b2mar:ISPSZone .
}
```
