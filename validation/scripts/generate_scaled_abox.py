#!/usr/bin/env python3
"""Generate scaled-N maritime ABoxes for both DMFO and B2-CCO.

Produces ABox files at validation/scale-test/{dmfo,b2cco}-maritime-N{N}.ttl
parameterised by N (number of synthetic containers, each replicating the
canonical port-call workflow + LCL deconsolidation scenario).

The base TBoxes (DMFO modules + maritime profile, B2-CCO base + maritime)
are reused unchanged. Only the ABox size scales.

Usage:
    python3 generate_scaled_abox.py 1 10 25 50 100
"""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime, timedelta

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'validation' / 'scale-test'
OUT.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────
# DMFO maritime ABox generator
# ─────────────────────────────────────────────────────────────────────

DMFO_HEADER = """\
@prefix dmfo:    <https://w3id.org/dmfo#> .
@prefix mar:     <https://w3id.org/dmfo/profiles/maritime#> .
@prefix ex:      <https://w3id.org/dmfo/profiles/maritime/scale#> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
@prefix prov:    <http://www.w3.org/ns/prov#> .
@prefix sosa:    <http://www.w3.org/ns/sosa/> .
@prefix dul:     <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#> .
@prefix geo:     <http://www.opengis.net/ont/geosparql#> .

<https://w3id.org/dmfo/profiles/maritime/scale-abox>
    a owl:Ontology ;
    owl:imports <https://w3id.org/dmfo/profiles/maritime> .

# Shared infrastructure (sites, regimes, agents, sensors)
ex:Berth_HHLA_CTA_03   a mar:Berth .
ex:Yard_CTA            a mar:TerminalYard .
ex:ISPSZone_CTA        a mar:ISPSZone ; geo:sfWithin ex:Yard_CTA .
ex:Gate_CTA_South      a mar:TerminalYard .
ex:CFS_CTA             a mar:CFS ; geo:sfWithin ex:Yard_CTA .
ex:Regime_EU_UCC       a mar:RegulatoryRegime .
ex:Regime_ISPS         a mar:RegulatoryRegime .
ex:Agent_CraneOp       a prov:Agent .
ex:Agent_GateController a prov:Agent .
ex:Agent_CFSOperator   a prov:Agent .
ex:Sensor_AIS          a sosa:Sensor .
ex:Sensor_OCR          a sosa:Sensor .
ex:Sensor_Thermo       a sosa:Sensor .

ex:Role_PredecessorState a prov:Role .
ex:Role_GroupageInput    a prov:Role .

"""

DMFO_PER_CONTAINER = """\
# ── Container {n} (full port-call + LCL deconsolidation) ──
ex:CONT_{n}  a mar:Container ;
    mar:bicCode          "HLXU{n:07d}" ;
    dmfo:identifierScheme "urn:iso:std:iso:6346"^^xsd:anyURI .

ex:Disch_{n}  a mar:VesselDischarge ;
    prov:startedAtTime  "{disch_start}"^^xsd:dateTime ;
    prov:endedAtTime    "{disch_end}"^^xsd:dateTime ;
    prov:wasAssociatedWith ex:Agent_CraneOp .

ex:CraneTrf_{n}  a mar:CraneTransfer ;
    prov:startedAtTime  "{crane_start}"^^xsd:dateTime ;
    prov:endedAtTime    "{crane_end}"^^xsd:dateTime ;
    prov:wasInformedBy  ex:Disch_{n} ;
    prov:wasAssociatedWith ex:Agent_CraneOp ;
    prov:qualifiedUsage [
        a prov:Usage ;
        prov:entity  ex:M_Discharged_{n} ;
        prov:hadRole ex:Role_PredecessorState
    ] .

ex:GateOut_{n}  a mar:GateMovement ;
    prov:startedAtTime  "{gate_start}"^^xsd:dateTime ;
    prov:wasInformedBy  ex:CraneTrf_{n} ;
    prov:wasAssociatedWith ex:Agent_GateController ;
    prov:qualifiedUsage [
        a prov:Usage ;
        prov:entity  ex:M_InYard_{n} ;
        prov:hadRole ex:Role_PredecessorState
    ] .

ex:Obs_AIS_{n}  a mar:Observation_AIS ;
    sosa:hasFeatureOfInterest ex:M_OnVessel_{n} ;
    sosa:resultTime "{disch_start}"^^xsd:dateTime ;
    sosa:phenomenonTime "{disch_start}"^^xsd:dateTime ;
    sosa:madeBySensor ex:Sensor_AIS .

ex:Obs_Disch_{n}  a mar:Observation_GateRead ;
    sosa:hasFeatureOfInterest ex:M_Discharged_{n} ;
    sosa:resultTime "{disch_end}"^^xsd:dateTime ;
    sosa:phenomenonTime "{disch_end}"^^xsd:dateTime .

ex:Obs_GateRead_{n}  a mar:Observation_GateRead ;
    sosa:hasFeatureOfInterest ex:M_GateOut_{n} ;
    sosa:resultTime "{gate_start}"^^xsd:dateTime ;
    sosa:phenomenonTime "{gate_start}"^^xsd:dateTime ;
    sosa:madeBySensor ex:Sensor_OCR .

ex:M_OnVessel_{n}  a mar:OnVessel ;
    dmfo:manifestationOf      ex:CONT_{n} ;
    dmfo:manifestationTimestamp "{vessel_ts}"^^xsd:dateTimeStamp .

ex:M_Discharged_{n}  a mar:Discharged ;
    dmfo:manifestationOf      ex:CONT_{n} ;
    dmfo:stateWasGeneratedBy  ex:Disch_{n} ;
    dmfo:evidencedBy          ex:Obs_Disch_{n} ;
    dmfo:manifestationTimestamp "{disch_end}"^^xsd:dateTimeStamp .

ex:M_InYard_{n}  a mar:InYard ;
    dmfo:manifestationOf      ex:CONT_{n} ;
    dmfo:stateWasGeneratedBy  ex:CraneTrf_{n} ;
    dmfo:manifestationTimestamp "{crane_end}"^^xsd:dateTimeStamp .

ex:M_GateOut_{n}  a mar:GateOut ;
    dmfo:manifestationOf      ex:CONT_{n} ;
    dmfo:stateWasGeneratedBy  ex:GateOut_{n} ;
    dmfo:evidencedBy          ex:Obs_GateRead_{n} ;
    dmfo:manifestationTimestamp "{gate_start}"^^xsd:dateTimeStamp .

# Custody + customs situations
ex:Sit_Custody_{n}  a mar:CustodyTransferSituation ;
    dul:includesObject ex:M_InYard_{n} , ex:M_Discharged_{n} ;
    dmfo:governedBy    ex:Regime_ISPS ;
    dmfo:situatedAt        ex:ISPSZone_CTA .

ex:Sit_Customs_{n}  a mar:CustomsControlSituation ;
    dul:includesObject ex:M_GateOut_{n} ;
    dmfo:governedBy    ex:Regime_EU_UCC ;
    dmfo:situatedAt        ex:Gate_CTA_South .

# LCL deconsolidation chain (every 5th container)
"""

DMFO_PER_LCL = """\
ex:CargoLot_BL_{n}  a mar:CargoLot , dmfo:SplitSourceIdentity ;
    dmfo:hasIdentifier "BL-{n}" ;
    dmfo:identifierScheme "urn:un:cefact:bl"^^xsd:anyURI .

ex:Decon_τ_{n}  a mar:DeconsolidationActivity ;
    prov:wasInformedBy ex:GateOut_{n} ;
    prov:wasAssociatedWith ex:Agent_CFSOperator ;
    prov:qualifiedUsage [
        a prov:Usage ;
        prov:entity  ex:M_GateOut_{n} ;
        prov:hadRole ex:Role_GroupageInput
    ] .

ex:CargoSubLot_{n}_a  a mar:CargoLot ;
    dmfo:hasIdentifier "HBL-{n}-A" ;
    prov:wasDerivedFrom ex:CargoLot_BL_{n} ;
    prov:wasGeneratedBy ex:Decon_τ_{n} .
ex:CargoSubLot_{n}_b  a mar:CargoLot ;
    dmfo:hasIdentifier "HBL-{n}-B" ;
    prov:wasDerivedFrom ex:CargoLot_BL_{n} ;
    prov:wasGeneratedBy ex:Decon_τ_{n} .
ex:CargoSubLot_{n}_c  a mar:CargoLot ;
    dmfo:hasIdentifier "HBL-{n}-C" ;
    prov:wasDerivedFrom ex:CargoLot_BL_{n} ;
    prov:wasGeneratedBy ex:Decon_τ_{n} .

ex:M_Distributed_{n}_a  a mar:Distributed ;
    dmfo:manifestationOf ex:CargoSubLot_{n}_a ;
    dmfo:stateWasGeneratedBy ex:Decon_τ_{n} ;
    dmfo:manifestationTimestamp "{decon_end}"^^xsd:dateTimeStamp .
ex:M_Distributed_{n}_b  a mar:Distributed ;
    dmfo:manifestationOf ex:CargoSubLot_{n}_b ;
    dmfo:stateWasGeneratedBy ex:Decon_τ_{n} ;
    dmfo:manifestationTimestamp "{decon_end}"^^xsd:dateTimeStamp .
ex:M_Distributed_{n}_c  a mar:Distributed ;
    dmfo:manifestationOf ex:CargoSubLot_{n}_c ;
    dmfo:stateWasGeneratedBy ex:Decon_τ_{n} ;
    dmfo:manifestationTimestamp "{decon_end}"^^xsd:dateTimeStamp .

"""

# Deliberate ACQ-IV gaps to keep classification meaningful
DMFO_GAPS = """\
# Class IV gaps (ABox-size-independent)
ex:CONT_GAP_evidence  a mar:Container ;
    mar:bicCode "GAPE0000001" ;
    dmfo:identifierScheme "urn:iso:std:iso:6346"^^xsd:anyURI .
ex:M_GAP_NoEvidence  a mar:InYard ;
    dmfo:manifestationOf ex:CONT_GAP_evidence ;
    dmfo:manifestationTimestamp "2026-04-12T10:00:00Z"^^xsd:dateTimeStamp .

ex:CONT_GAP_causal  a mar:Container ;
    mar:bicCode "GAPC0000002" ;
    dmfo:identifierScheme "urn:iso:std:iso:6346"^^xsd:anyURI .
ex:M_GAP_NoCausal  a mar:InYard ;
    dmfo:manifestationOf ex:CONT_GAP_causal ;
    dmfo:manifestationTimestamp "2026-04-12T11:00:00Z"^^xsd:dateTimeStamp .

ex:CONT_GAP_scheme  a mar:Container ;
    mar:bicCode "GAPS0000003" .

ex:Sit_GAP_governance  a dul:Situation ;
    dul:includesObject ex:M_GAP_NoEvidence ;
    dmfo:situatedAt ex:Yard_CTA .
"""


def generate_dmfo_maritime(n: int, out_path: Path):
    base = datetime(2026, 4, 12, 8, 0)
    parts = [DMFO_HEADER]
    for i in range(1, n + 1):
        offset = timedelta(minutes=i * 7)
        parts.append(DMFO_PER_CONTAINER.format(
            n=i,
            disch_start=(base + offset).isoformat() + 'Z',
            disch_end=(base + offset + timedelta(minutes=6)).isoformat() + 'Z',
            crane_start=(base + offset + timedelta(minutes=6)).isoformat() + 'Z',
            crane_end=(base + offset + timedelta(minutes=10)).isoformat() + 'Z',
            gate_start=(base + offset + timedelta(hours=4)).isoformat() + 'Z',
            vessel_ts=(base + offset - timedelta(minutes=30)).isoformat() + 'Z',
        ))
        if i % 5 == 0:  # LCL split every 5th container
            parts.append(DMFO_PER_LCL.format(
                n=i,
                decon_end=(base + offset + timedelta(hours=8)).isoformat() + 'Z',
            ))
    parts.append(DMFO_GAPS)
    out_path.write_text(''.join(parts))


# ─────────────────────────────────────────────────────────────────────
# B2-CCO maritime ABox generator
# ─────────────────────────────────────────────────────────────────────

B2_HEADER = """\
@prefix b2cco:  <https://w3id.org/dmfo/baseline/cco#> .
@prefix b2mar:  <https://w3id.org/dmfo/baseline/cco/maritime#> .
@prefix bfo:    <http://purl.obolibrary.org/obo/> .
@prefix cco:    <https://www.commoncoreontologies.org/> .
@prefix ex:     <https://w3id.org/dmfo/baseline/cco/maritime/scale#> .
@prefix sosa:   <http://www.w3.org/ns/sosa/> .
@prefix owl:    <http://www.w3.org/2002/07/owl#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .

<https://w3id.org/dmfo/baseline/cco/maritime/scale-abox>
    a owl:Ontology ;
    owl:imports <https://w3id.org/dmfo/baseline/cco/maritime> .

ex:Berth_HHLA_CTA_03   a b2mar:Berth .
ex:Yard_CTA            a b2mar:TerminalYard .
ex:ISPSZone_CTA        a b2mar:ISPSZone ; bfo:BFO_0000171 ex:Yard_CTA .
ex:Gate_CTA_South      a b2mar:TerminalYard .
ex:CFS_CTA             a b2mar:CFS ; bfo:BFO_0000171 ex:Yard_CTA .
ex:Agent_CraneOp       a cco:ont00001017 .
ex:Agent_GateController a cco:ont00001017 .
ex:Agent_CFSOperator   a cco:ont00001017 .
ex:Sensor_AIS          a sosa:Sensor .
ex:Sensor_OCR          a sosa:Sensor .

"""

B2_PER_CONTAINER = """\
ex:CONT_{n}  a b2mar:Container .
ex:BIC_{n}   a b2mar:BICCode ;
    cco:ont00001916 ex:CONT_{n} ;
    rdfs:label "HLXU{n:07d}" .

ex:Q_{n}_OnVessel    a b2mar:OnVesselLocationQuality ; bfo:BFO_0000197 ex:CONT_{n} .
ex:Q_{n}_Discharged  a b2mar:DischargedLocationQuality ; bfo:BFO_0000197 ex:CONT_{n} .
ex:Q_{n}_InYard      a b2mar:InYardLocationQuality ; bfo:BFO_0000197 ex:CONT_{n} .
ex:Q_{n}_GateOut     a b2mar:GateOutLocationQuality ; bfo:BFO_0000197 ex:CONT_{n} .

ex:Disch_{n}  a b2mar:VesselDischarge ;
    cco:ont00001833 ex:Agent_CraneOp ;
    cco:ont00001986 ex:Q_{n}_Discharged ;
    cco:ont00001918 ex:Berth_HHLA_CTA_03 .

ex:CraneTrf_{n}  a b2mar:CraneTransfer ;
    cco:ont00001833 ex:Agent_CraneOp ;
    cco:ont00001986 ex:Q_{n}_InYard ;
    cco:ont00001921 ex:Q_{n}_Discharged ;
    cco:ont00001918 ex:Yard_CTA ;
    bfo:BFO_0000062 ex:Disch_{n} .

ex:GateOut_{n}  a b2mar:GateMovement ;
    cco:ont00001833 ex:Agent_GateController ;
    cco:ont00001986 ex:Q_{n}_GateOut ;
    cco:ont00001921 ex:Q_{n}_InYard ;
    cco:ont00001918 ex:Gate_CTA_South ;
    bfo:BFO_0000062 ex:CraneTrf_{n} .

ex:Obs_AIS_{n}      a sosa:Observation ;
    sosa:hasFeatureOfInterest ex:Q_{n}_OnVessel ;
    sosa:resultTime "{disch_start}"^^xsd:dateTime ;
    sosa:phenomenonTime "{disch_start}"^^xsd:dateTime ;
    sosa:madeBySensor ex:Sensor_AIS .

ex:Obs_Disch_{n}    a sosa:Observation ;
    sosa:hasFeatureOfInterest ex:Q_{n}_Discharged ;
    sosa:resultTime "{disch_end}"^^xsd:dateTime ;
    sosa:phenomenonTime "{disch_end}"^^xsd:dateTime .

ex:Obs_GateRead_{n} a sosa:Observation ;
    sosa:hasFeatureOfInterest ex:Q_{n}_GateOut ;
    sosa:resultTime "{gate_start}"^^xsd:dateTime ;
    sosa:phenomenonTime "{gate_start}"^^xsd:dateTime ;
    sosa:madeBySensor ex:Sensor_OCR .

# Variant-b Measurement ICEs (parallel, for native variant)
ex:Meas_AIS_{n}      a b2mar:AIS_Measurement ;
    cco:ont00001808 ex:Q_{n}_OnVessel .
ex:Meas_GateRead_{n} a b2mar:GateRead_Measurement ;
    cco:ont00001808 ex:Q_{n}_GateOut .
ex:Meas_Disch_{n}    a b2mar:GateRead_Measurement ;
    cco:ont00001808 ex:Q_{n}_Discharged .

ex:CustodyTransfer_{n}  a b2mar:CustodyTransfer_Act ;
    bfo:BFO_0000171 ex:ISPSZone_CTA .
ex:CustomsControl_{n}   a b2mar:CustomsControl_Act ;
    bfo:BFO_0000171 ex:Gate_CTA_South .
"""

B2_REGIMES_SHARED = """\
ex:Regime_EU_UCC  a b2mar:RegulatoryRegime .
ex:Regime_ISPS    a b2mar:RegulatoryRegime .
"""

B2_PER_REGIME_LINK = """\
ex:Regime_EU_UCC cco:ont00001942 ex:CustomsControl_{n} .
ex:Regime_ISPS   cco:ont00001942 ex:CustodyTransfer_{n} .
"""

B2_PER_LCL = """\
ex:CargoLot_BL_{n}  a b2mar:CargoLot .
ex:Identifier_BL_{n}  a cco:ont00000292 ;
    cco:ont00001916 ex:CargoLot_BL_{n} ;
    rdfs:label "BL-{n}" .

ex:CargoSubLot_{n}_a  a b2mar:CargoLot .
ex:CargoSubLot_{n}_b  a b2mar:CargoLot .
ex:CargoSubLot_{n}_c  a b2mar:CargoLot .

ex:Q_{n}_a_Distributed  a b2mar:DistributedLocationQuality ; bfo:BFO_0000197 ex:CargoSubLot_{n}_a .
ex:Q_{n}_b_Distributed  a b2mar:DistributedLocationQuality ; bfo:BFO_0000197 ex:CargoSubLot_{n}_b .
ex:Q_{n}_c_Distributed  a b2mar:DistributedLocationQuality ; bfo:BFO_0000197 ex:CargoSubLot_{n}_c .

ex:Decon_τ_{n}  a b2mar:DeconsolidationActivity ;
    cco:ont00001833 ex:Agent_CFSOperator ;
    cco:ont00001921 ex:CargoLot_BL_{n} ;
    cco:ont00001986 ex:CargoSubLot_{n}_a , ex:CargoSubLot_{n}_b , ex:CargoSubLot_{n}_c ,
                    ex:Q_{n}_a_Distributed , ex:Q_{n}_b_Distributed , ex:Q_{n}_c_Distributed ;
    cco:ont00001918 ex:CFS_CTA ;
    bfo:BFO_0000062 ex:GateOut_{n} .

"""

B2_GAPS = """\
# Class IV gaps
ex:CONT_GAP_evidence  a b2mar:Container .
ex:BIC_GAP_evidence   a b2mar:BICCode ; cco:ont00001916 ex:CONT_GAP_evidence ; rdfs:label "GAPE0000001" .
ex:Q_GAP_NoEvidence   a b2mar:InYardLocationQuality ; bfo:BFO_0000197 ex:CONT_GAP_evidence .

ex:CONT_GAP_causal    a b2mar:Container .
ex:BIC_GAP_causal     a b2mar:BICCode ; cco:ont00001916 ex:CONT_GAP_causal ; rdfs:label "GAPC0000002" .
ex:Q_GAP_NoCausal     a b2mar:InYardLocationQuality ; bfo:BFO_0000197 ex:CONT_GAP_causal .

ex:CONT_GAP_scheme    a b2mar:Container .

ex:Sit_GAP_governance a cco:ont00000005 ; bfo:BFO_0000171 ex:Yard_CTA .
"""


def generate_b2cco_maritime(n: int, out_path: Path):
    base = datetime(2026, 4, 12, 8, 0)
    parts = [B2_HEADER, B2_REGIMES_SHARED]
    for i in range(1, n + 1):
        offset = timedelta(minutes=i * 7)
        parts.append(B2_PER_CONTAINER.format(
            n=i,
            disch_start=(base + offset).isoformat() + 'Z',
            disch_end=(base + offset + timedelta(minutes=6)).isoformat() + 'Z',
            gate_start=(base + offset + timedelta(hours=4)).isoformat() + 'Z',
        ))
        parts.append(B2_PER_REGIME_LINK.format(n=i))
        if i % 5 == 0:
            parts.append(B2_PER_LCL.format(n=i))
    parts.append(B2_GAPS)
    out_path.write_text(''.join(parts))


def main():
    sizes = [int(x) for x in sys.argv[1:]] or [1, 10, 25, 50, 100]
    print(f'Generating scaled ABoxes for N ∈ {sizes}')
    for n in sizes:
        dp = OUT / f'dmfo-maritime-N{n:03d}.ttl'
        bp = OUT / f'b2cco-maritime-N{n:03d}.ttl'
        generate_dmfo_maritime(n, dp)
        generate_b2cco_maritime(n, bp)
        # Quick triple count
        from rdflib import Graph
        gd = Graph(); gd.parse(dp, format='turtle')
        gb = Graph(); gb.parse(bp, format='turtle')
        print(f'  N={n:3d}  DMFO={len(gd):>5d}t  B2-CCO={len(gb):>5d}t  '
              f'(ratio {len(gd)/len(gb):.2f}x)')


if __name__ == '__main__':
    main()
