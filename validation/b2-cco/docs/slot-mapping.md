# DMFO Slot → CCO Pattern Mapping

CCO 2.0 IRIs verified against
[`../vendor/cco-2.0-mapping.csv`](../vendor/cco-2.0-mapping.csv) and the
merged CCO TTL (`vendor/cco-2.0/src/cco-merged/CommonCoreOntologiesMerged.ttl`).
"Source" cites the FOIS 2024 paper section + the Modeling-with-CCO
guide page; "ADR" links the architecture decision record.

## Anchor classes

| DMFO slot | DMFO anchor | CCO / BFO pendant | IRI | Source | ADR |
|---|---|---|---|---|---|
| Identity | `dmfo:TimeVaryingEntity` | `bfo:object` (BFO_0000030); domain subclass under `cco:Container` for maritime, `cco:Agent` for persons. CCO has no umbrella "Time-Varying Entity" class. | `http://purl.obolibrary.org/obo/BFO_0000030` | Jensen et al. 2024 §3 (Object Ontology); BFO ISO/IEC 21838-2 | ADR-001 |
| State | `dmfo:Manifestation` | **No direct equivalent.** Modelled as `cco:Stasis of Quality` over a `bfo:Quality` that `bfo:inheres in` the Identity object, with optional `bfo:Process Profile` for state-bearing process phases. | `https://www.commoncoreontologies.org/ont00000850` (Stasis of Quality) + `http://purl.obolibrary.org/obo/BFO_0000019` (Quality) | Jensen et al. 2024 §3.2 (Quality pattern); MwCCO 2024 §4 | ADR-001 |
| Activity | `prov:Activity` | `cco:Act` (intentional act, requires agent) **or** `bfo:process` for non-intentional processes. Maritime uses `cco:Act` for crane / vessel operations. | `https://www.commoncoreontologies.org/ont00000005` (Act); `http://purl.obolibrary.org/obo/BFO_0000015` (Process) | Jensen et al. 2024 §4 (Event Ontology) | ADR-002 |
| Agent | `prov:Agent` | `cco:Agent` (material entity capable of intentional acts). | `https://www.commoncoreontologies.org/ont00001017` | Jensen et al. 2024 §4 | ADR-002 |
| Evidence | `sosa:Observation` | **NONE — fallback needed.** Two variants: (a) co-import SOSA into CCO (ADR-003a, isolated extension); (b) CCO-native `cco:Measurement Information Content Entity` + `bfo:realizable entity` measurement-process pattern (ADR-003b). | (a) `http://www.w3.org/ns/sosa/Observation`; (b) `https://www.commoncoreontologies.org/ont00001163` | Jensen et al. 2024 (no SOSA integration); MwCCO 2024 §6 (measurement pattern) | ADR-003a, ADR-003b |
| Context | `dul:Situation`/`dul:Description` | `cco:Process Regulation` (subclass of `cco:Prescriptive Information Content Entity`); CCO has no native `Situation` class. The "situation" is encoded as the `cco:Act` token that the regulation `cco:prescribes`. | `https://www.commoncoreontologies.org/ont00001324` (Process Regulation) + `https://www.commoncoreontologies.org/ont00000965` (Prescriptive ICE) | Jensen et al. 2024 §5 (Information Entity Ontology) | ADR-004 |
| Location | `geo:Feature` | `cco:Geospatial Region` for spatial regions; `bfo:Site` for institutional zones; **no native topology**. GeoSPARQL `sfWithin` not natively expressible. | `https://www.commoncoreontologies.org/ont00000472` (Geospatial Region) + `http://purl.obolibrary.org/obo/BFO_0000029` (Site) | Jensen et al. 2024 §6 (Geospatial Ontology); BFO ISO §4.4 | ADR-005 |

## Object properties

CCO/BFO uses generic, broadly-typed properties; B2-CCO must not narrow
their domain/range to fresh subclasses (Faithful-Translation-Rule F3).

| DMFO bridge | A_id | CCO/BFO property reused (no narrowing) | IRI | Notes |
|---|---|---|---|---|
| `dmfo:manifestationOf` | A2 | `bfo:inheres in` (BFO_0000197), inverse of `bfo:has quality` | `http://purl.obolibrary.org/obo/BFO_0000197` | Quality inheres in the bearer (the Identity object). |
| `dmfo:stateWasGeneratedBy` | A5 | `cco:has output` (the activity has the quality as an output) **or** `cco:has process part` for stage-of-process. | `https://www.commoncoreontologies.org/ont00001986` / `https://www.commoncoreontologies.org/ont00001777` | No subproperty of `prov:wasGeneratedBy` because PROV-O is not co-imported in baseline. |
| `dmfo:evidencedBy` | A3 | (a) `sosa:hasFeatureOfInterest`-inverse if SOSA co-imported; (b) `cco:is about` (Measurement ICE about the Quality). | (a) `http://www.w3.org/ns/sosa/hasFeatureOfInterest`; (b) `https://www.commoncoreontologies.org/ont00001808` | ADR-003 variants. |
| `dmfo:governedBy` | A4 | `cco:prescribes` (Process Regulation prescribes the Act). | `https://www.commoncoreontologies.org/ont00001942` | NB: prescribes goes from regulation to act, opposite direction of DMFO `governedBy`. SPARQL must reflect the inversion. |
| `dmfo:inZone` | A6 | `bfo:located in` (BFO_0000171) — there is no GeoSPARQL `sfWithin` semantics. | `http://purl.obolibrary.org/obo/BFO_0000171` | Spatial-region containment is BFO-mereotopological, not GeoSPARQL-typed. |

## Domain classes (maritime)

| DMFO maritime class | B2-CCO domain class | Parent | Notes |
|---|---|---|---|
| `mar:Container` | `b2mar:Container` | `cco:Container` (`ont00000020`) | CCO has a native "Container" class. |
| `mar:Vessel` | `b2mar:Vessel` | `bfo:object` | CCO 2.0 has no `Vessel`; we subclass under BFO Object. |
| `mar:CraneTransfer` | `b2mar:CraneTransfer` | `cco:Act` | Intentional act with agent (crane operator). |
| `mar:VesselDischarge` | `b2mar:VesselDischarge` | `cco:Act` | |
| `mar:GateMovement` | `b2mar:GateMovement` | `cco:Act` | |
| `mar:Observation_AIS` | `b2mar:AIS_Measurement` | `cco:Measurement Information Content Entity` (`ont00001163`) | ADR-003b path. |
| `mar:CustodyTransferSituation` | `b2mar:CustodyTransfer_Act` | `cco:Act` | Re-shaped: the "situation" is reified as the act itself, not a separate situation class. |
| `mar:RegulatoryRegime` | `b2mar:RegulatoryRegime` | `cco:Process Regulation` (`ont00001324`) | |
| `mar:ISPSZone` | `b2mar:ISPSZone` | `bfo:Site` (`BFO_0000029`) | |
| `mar:TerminalYard` | `b2mar:TerminalYard` | `bfo:Site` | |

## Documented absences (slots without native CCO pendant)

* **State as a class.** CCO has `Stasis of Quality` for stable
  intervals but not a single "state of an entity at a moment" class.
  Quality-inherence is the closest pattern.
* **Situation.** CCO has no `Situation` class equivalent to
  `dul:Situation`. Contextual situations are reified through the act
  + regulation pattern.
* **Observation as a typed event with feature-of-interest.** CCO has
  `Measurement ICE` (information about a measurement) but no native
  reified observation event with a typed `hasFeatureOfInterest` link.
  `cco:is about` is the closest, but it relates an ICE to its subject
  generically.
* **GeoSPARQL spatial relations.** `sfWithin`, `sfIntersects`,
  `sfTouches` etc. have no CCO/BFO equivalents. Only mereotopological
  `located in` / `has spatial part` are available.
