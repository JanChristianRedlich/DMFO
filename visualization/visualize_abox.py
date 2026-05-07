#!/usr/bin/env python3
"""
DMFO ABox Graph Visualization
=============================
Loads a profile ABox (Turtle) plus its DMFO TBox closure and renders
an interactive HTML graph (vis.js) coloured by the six DMFO slots and
the typed bridges.

Default behaviour produces two HTML files — one for the maritime
profile and one for the food profile — under ``visualization/results/``.

Usage:
    python visualization/visualize_abox.py                         # both profiles
    python visualization/visualize_abox.py --profile maritime
    python visualization/visualize_abox.py --profile food
    python visualization/visualize_abox.py --abox path/to/abox.ttl --output out.html

Requirements: ``pip install rdflib``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

try:
    import rdflib
    from rdflib import BNode, Literal, URIRef
    from rdflib.namespace import RDF, RDFS
except ImportError:
    print("ERROR: rdflib fehlt. pip install rdflib", file=sys.stderr)
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO / "visualization" / "results"

# Paper-strict profile bundles. Each entry = list of TTL files merged
# into a single rdflib Graph for visualisation. The TBox files are
# included so subClassOf chains classify the ABox individuals into the
# six DMFO slots (otherwise mar:/food:/ex: individuals would all fall
# into the "abox_vocab" bucket).
PROFILES: dict[str, dict] = {
    "maritime": {
        "label": "Maritime profile (port-call sequence)",
        "files": [
            REPO / "ontology" / "dmfo-base.ttl",
            REPO / "ontology" / "dmfo-identity.ttl",
            REPO / "ontology" / "dmfo-state.ttl",
            REPO / "ontology" / "dmfo-evidence.ttl",
            REPO / "ontology" / "dmfo-context.ttl",
            REPO / "ontology" / "dmfo-activity.ttl",
            REPO / "ontology" / "dmfo-location.ttl",
            REPO / "ontology" / "dmfo-identity-deriv.ttl",
            REPO / "profiles" / "maritime" / "mar-tbox.ttl",
            REPO / "profiles" / "maritime" / "mar-abox.ttl",
        ],
        "abox_only": [REPO / "profiles" / "maritime" / "mar-abox.ttl"],
        "subject_filter": "https://w3id.org/dmfo/profiles/maritime/example",
    },
    "food": {
        "label": "Food profile (FSMA-204 split/merge)",
        "files": [
            REPO / "ontology" / "dmfo-base.ttl",
            REPO / "ontology" / "dmfo-identity.ttl",
            REPO / "ontology" / "dmfo-state.ttl",
            REPO / "ontology" / "dmfo-evidence.ttl",
            REPO / "ontology" / "dmfo-context.ttl",
            REPO / "ontology" / "dmfo-activity.ttl",
            REPO / "ontology" / "dmfo-location.ttl",
            REPO / "ontology" / "dmfo-identity-deriv.ttl",
            REPO / "profiles" / "food" / "food-tbox.ttl",
            REPO / "profiles" / "food" / "food-abox.ttl",
        ],
        "abox_only": [REPO / "profiles" / "food" / "food-abox.ttl"],
        "subject_filter": "https://w3id.org/dmfo/profiles/food/example",
    },
}

VIS_NETWORK_CDN = "https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"

COLORS: dict[str, str] = {
    "identity_dim": "#e5989b",
    "state_dim": "#74b9ff",
    "location_dim": "#55efc4",
    "activity_dim": "#fdcb6e",
    "context_dim": "#a29bfe",
    "evidence_dim": "#fab1a0",
    "bridge_state_identity": "#0984e3",   # A2 manifestationOf
    "bridge_state_activity": "#e17055",   # A5 stateWasGeneratedBy / prov:wasGeneratedBy
    "bridge_state_evidence": "#6c5ce7",   # A3 evidencedBy
    "bridge_situation_zone": "#00b894",   # A6 inZone / geo:sfWithin
    "bridge_situation_regime": "#fd79a8", # A4 governedBy
    "bridge_identity_deriv": "#d63031",   # SplitSourceIdentity / MergeSourceIdentity / wasDerivedFrom
    "core_dmfo": "#dfe6e9",
    "provenance": "#636e72",
    "meta_rdf": "#b2bec3",
    "abox_vocab": "#dcdde1",
    "literal": "#95a5a6",
    "other": "#576574",
}

FILTER_CATEGORY_ORDER: list[str] = [
    "identity_dim",
    "state_dim",
    "location_dim",
    "activity_dim",
    "context_dim",
    "evidence_dim",
    "bridge_state_identity",
    "bridge_state_activity",
    "bridge_state_evidence",
    "bridge_situation_zone",
    "bridge_situation_regime",
    "bridge_identity_deriv",
    "core_dmfo",
    "provenance",
    "meta_rdf",
    "abox_vocab",
    "literal",
    "other",
]

CATEGORY_LABELS_DE: dict[str, str] = {
    "identity_dim": "Identity (TVE)",
    "state_dim": "State / Manifestation",
    "location_dim": "Location (geo:Feature)",
    "activity_dim": "Activity (prov:Activity)",
    "context_dim": "Context (dul:Situation/Description)",
    "evidence_dim": "Evidence (sosa:Observation)",
    "bridge_state_identity": "Bridge A2: manifestationOf",
    "bridge_state_activity": "Bridge A5: stateWasGeneratedBy",
    "bridge_state_evidence": "Bridge A3: evidencedBy",
    "bridge_situation_zone": "Bridge A6: inZone",
    "bridge_situation_regime": "Bridge A4: governedBy",
    "bridge_identity_deriv": "Identity-Derivation (Split/Merge)",
    "core_dmfo": "DMFO core",
    "provenance": "PROV / Agent",
    "meta_rdf": "RDF/RDFS/OWL/SKOS",
    "abox_vocab": "Profile-Vokabular",
    "literal": "Literal",
    "other": "Sonstiges",
}

# Paper-strict predicate-to-category mapping. The five DMFO bridges are
# the only ``dmfo:`` object properties; everything else routes through
# imported vocabularies.
PREDICATE_CATEGORY: dict[str, str] = {
    "https://w3id.org/dmfo#manifestationOf": "bridge_state_identity",
    "https://w3id.org/dmfo#stateWasGeneratedBy": "bridge_state_activity",
    "https://w3id.org/dmfo#evidencedBy": "bridge_state_evidence",
    "https://w3id.org/dmfo#inZone": "bridge_situation_zone",
    "https://w3id.org/dmfo#governedBy": "bridge_situation_regime",
    "https://w3id.org/dmfo#manifestationTimestamp": "state_dim",
    "https://w3id.org/dmfo#hasIdentifier": "identity_dim",
    # Identity-derivation pattern (PROV-O backbone)
    "http://www.w3.org/ns/prov#wasDerivedFrom": "bridge_identity_deriv",
    "http://www.w3.org/ns/prov#hadPrimarySource": "bridge_identity_deriv",
    # PROV-O activity backbone
    "http://www.w3.org/ns/prov#wasGeneratedBy": "bridge_state_activity",
    "http://www.w3.org/ns/prov#wasInformedBy": "bridge_state_activity",
    "http://www.w3.org/ns/prov#used": "activity_dim",
    "http://www.w3.org/ns/prov#wasAssociatedWith": "activity_dim",
    "http://www.w3.org/ns/prov#qualifiedUsage": "activity_dim",
    "http://www.w3.org/ns/prov#qualifiedAssociation": "activity_dim",
    "http://www.w3.org/ns/prov#hadRole": "activity_dim",
    "http://www.w3.org/ns/prov#agent": "provenance",
    "http://www.w3.org/ns/prov#entity": "identity_dim",
    "http://www.w3.org/ns/prov#startedAtTime": "activity_dim",
    "http://www.w3.org/ns/prov#endedAtTime": "activity_dim",
    # SOSA observation backbone
    "http://www.w3.org/ns/sosa/hasFeatureOfInterest": "bridge_state_evidence",
    "http://www.w3.org/ns/sosa/observedProperty": "evidence_dim",
    "http://www.w3.org/ns/sosa/madeBySensor": "evidence_dim",
    "http://www.w3.org/ns/sosa/hasResult": "evidence_dim",
    "http://www.w3.org/ns/sosa/resultTime": "evidence_dim",
    "http://www.w3.org/ns/sosa/phenomenonTime": "evidence_dim",
    # DUL/DnS situation/description
    "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#satisfies": "bridge_situation_regime",
    "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#hasSetting": "context_dim",
    "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#includesObject": "context_dim",
    "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#defines": "context_dim",
    # GeoSPARQL spatial
    "http://www.opengis.net/ont/geosparql#sfWithin": "bridge_situation_zone",
    "http://www.opengis.net/ont/geosparql#sfContains": "location_dim",
    "http://www.opengis.net/ont/geosparql#hasGeometry": "location_dim",
    # OWL-Time
    "http://www.w3.org/2006/time#before": "state_dim",
    "http://www.w3.org/2006/time#after": "state_dim",
    "http://www.w3.org/2006/time#hasBeginning": "state_dim",
    "http://www.w3.org/2006/time#hasEnd": "state_dim",
    "http://www.w3.org/2006/time#inXSDDateTimeStamp": "state_dim",
}

PREDICATE_NS_FALLBACK: list[tuple[str, str]] = [
    ("https://w3id.org/dmfo#", "core_dmfo"),
    ("http://www.w3.org/ns/prov#", "provenance"),
    ("http://www.w3.org/ns/sosa/", "evidence_dim"),
    ("http://www.w3.org/ns/ssn/", "evidence_dim"),
    ("http://www.ontologydesignpatterns.org/ont/dul/", "context_dim"),
    ("http://www.opengis.net/ont/geosparql#", "location_dim"),
    ("http://www.w3.org/2006/time#", "state_dim"),
    ("https://w3id.org/dmfo/profiles/maritime", "abox_vocab"),
    ("https://w3id.org/dmfo/profiles/food", "abox_vocab"),
    ("http://purl.org/dc/terms/", "meta_rdf"),
    ("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "meta_rdf"),
    ("http://www.w3.org/2002/07/owl#", "meta_rdf"),
    ("http://www.w3.org/2000/01/rdf-schema#", "meta_rdf"),
    ("http://www.w3.org/2004/02/skos/core#", "meta_rdf"),
]

# Type → slot category. Anchor classes (paper Table 1) and their
# imported-vocabulary super-classes both classify into the right slot.
TYPE_CATEGORY: dict[str, str] = {
    "https://w3id.org/dmfo#TimeVaryingEntity": "identity_dim",
    "https://w3id.org/dmfo#Manifestation": "state_dim",
    "https://w3id.org/dmfo#SplitSourceIdentity": "bridge_identity_deriv",
    "https://w3id.org/dmfo#MergeSourceIdentity": "bridge_identity_deriv",
    "http://www.w3.org/ns/prov#Entity": "identity_dim",
    "http://www.w3.org/ns/prov#Activity": "activity_dim",
    "http://www.w3.org/ns/prov#Agent": "provenance",
    "http://www.w3.org/ns/prov#Usage": "activity_dim",
    "http://www.w3.org/ns/prov#Association": "activity_dim",
    "http://www.w3.org/ns/prov#Role": "activity_dim",
    "http://www.w3.org/ns/sosa/Observation": "evidence_dim",
    "http://www.w3.org/ns/sosa/Sensor": "evidence_dim",
    "http://www.w3.org/ns/sosa/FeatureOfInterest": "state_dim",
    "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Situation": "context_dim",
    "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Description": "context_dim",
    "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Event": "activity_dim",
    "http://www.opengis.net/ont/geosparql#Feature": "location_dim",
    "http://www.opengis.net/ont/geosparql#SpatialObject": "location_dim",
    "http://www.w3.org/2006/time#Instant": "state_dim",
    "http://www.w3.org/2006/time#Interval": "state_dim",
}

TYPE_NS_FALLBACK: list[tuple[str, str]] = [
    ("https://w3id.org/dmfo#", "core_dmfo"),
    ("http://www.w3.org/ns/prov#", "provenance"),
    ("http://www.w3.org/ns/sosa/", "evidence_dim"),
    ("http://www.w3.org/ns/ssn/", "evidence_dim"),
    ("http://www.ontologydesignpatterns.org/ont/dul/", "context_dim"),
    ("http://www.opengis.net/ont/geosparql#", "location_dim"),
    ("http://www.w3.org/2006/time#", "state_dim"),
]

# Larger numbers → higher priority when an individual has multiple types.
TYPE_PRIORITY: dict[str, int] = {
    "https://w3id.org/dmfo#Manifestation": 100,
    "https://w3id.org/dmfo#TimeVaryingEntity": 95,
    "https://w3id.org/dmfo#SplitSourceIdentity": 90,
    "https://w3id.org/dmfo#MergeSourceIdentity": 90,
    "http://www.w3.org/ns/sosa/Observation": 85,
    "http://www.w3.org/ns/prov#Activity": 80,
    "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Situation": 75,
    "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Description": 70,
    "http://www.opengis.net/ont/geosparql#Feature": 65,
    "http://www.w3.org/ns/prov#Agent": 60,
}


def term_id(term) -> str:
    if isinstance(term, URIRef):
        return str(term)
    if isinstance(term, BNode):
        return str(term)
    if isinstance(term, Literal):
        h = hashlib.sha256(str(term).encode("utf-8")).hexdigest()[:12]
        return f"literal:{h}"
    return str(term)


def short_name(term) -> str:
    if isinstance(term, URIRef):
        s = str(term)
        if "#" in s:
            return s.rsplit("#", 1)[-1]
        return s.rsplit("/", 1)[-1]
    if isinstance(term, BNode):
        return str(term)
    if isinstance(term, Literal):
        t = str(term)
        return (t[:60] + "…") if len(t) > 60 else t
    return str(term)[:40]


def predicate_label(p: URIRef) -> str:
    s = str(p)
    if "#" in s:
        return s.rsplit("#", 1)[-1]
    return s.rsplit("/", 1)[-1]


def category_for_predicate(pred_uri: str) -> str:
    if pred_uri in PREDICATE_CATEGORY:
        return PREDICATE_CATEGORY[pred_uri]
    for prefix, cat in PREDICATE_NS_FALLBACK:
        if pred_uri.startswith(prefix):
            return cat
    return "other"


def category_for_type(type_uri: str) -> str:
    if type_uri in TYPE_CATEGORY:
        return TYPE_CATEGORY[type_uri]
    for prefix, cat in TYPE_NS_FALLBACK:
        if type_uri.startswith(prefix):
            return cat
    return "other"


def load_labels(g: rdflib.Graph) -> dict[str, str]:
    out: dict[str, str] = {}
    for subj, _, lit in g.triples((None, RDFS.label, None)):
        if isinstance(subj, (URIRef, BNode)) and isinstance(lit, Literal):
            sid = term_id(subj)
            val = str(lit)
            if len(val) > 80:
                val = val[:77] + "…"
            out[sid] = val
    return out


def types_by_node_id(g: rdflib.Graph) -> dict[str, list[str]]:
    m: dict[str, list[str]] = {}
    for s, _, o in g.triples((None, RDF.type, None)):
        if not isinstance(o, URIRef):
            continue
        if isinstance(s, Literal):
            continue
        sid = term_id(s)
        m.setdefault(sid, []).append(str(o))
    return m


def pick_node_category(nid: str, types_map: dict[str, list[str]]) -> str:
    if nid.startswith("literal:"):
        return "literal"
    types = types_map.get(nid, [])
    if not types:
        if nid.startswith("https://w3id.org/dmfo/profiles/"):
            return "abox_vocab"
        return "other"
    best_t = max(types, key=lambda t: TYPE_PRIORITY.get(t, 0))
    return category_for_type(best_t)


def font_color_for_bg(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#1a1a1e" if luminance > 0.55 else "#f5f6fa"


def collect_edges(
    g: rdflib.Graph,
    *,
    include_literals: bool,
    subject_prefixes: list[str] | None,
) -> tuple[list[tuple[str, str, str, str, str]], dict[str, str]]:
    edges: list[tuple[str, str, str, str, str]] = []
    literal_labels: dict[str, str] = {}
    for s, p, o in g:
        if not isinstance(p, URIRef):
            continue
        if isinstance(s, Literal):
            continue
        sid = term_id(s)
        if subject_prefixes and isinstance(s, URIRef):
            if not any(str(s).startswith(pref) for pref in subject_prefixes):
                continue

        if isinstance(o, Literal):
            if not include_literals:
                continue
            oid = term_id(o)
            if oid not in literal_labels:
                literal_labels[oid] = short_name(o)
            plab = predicate_label(p)
            edges.append((sid, oid, str(p), plab, str(p)))
        elif isinstance(o, (URIRef, BNode)):
            oid = term_id(o)
            plab = predicate_label(p)
            edges.append((sid, oid, str(p), plab, str(p)))
    return edges, literal_labels


def build_vis_data(
    edges: list[tuple[str, str, str, str, str]],
    labels_by_id: dict[str, str],
    types_map: dict[str, list[str]],
) -> tuple[list[dict], list[dict]]:
    node_ids: set[str] = set()
    for sid, oid, _, _, _ in edges:
        node_ids.add(sid)
        node_ids.add(oid)

    nodes: list[dict] = []
    for nid in sorted(node_ids):
        ncat = pick_node_category(nid, types_map)
        bg = COLORS.get(ncat, COLORS["other"])
        fcol = font_color_for_bg(bg)
        label = labels_by_id.get(nid)
        if not label:
            if nid.startswith("literal:"):
                label = labels_by_id.get(nid, nid)
            else:
                label = short_name(URIRef(nid)) if nid.startswith("http") else nid[:48]
        title = f"{nid}\n[Kategorie: {ncat}]"
        nodes.append(
            {
                "id": nid,
                "label": label,
                "title": title,
                "color": bg,
                "font": {"color": fcol},
                "dmfoNodeCat": ncat,
            }
        )

    vis_edges: list[dict] = []
    seen_pairs: set[tuple[str, str, str]] = set()
    ei = 0
    for sid, oid, puri, plab, ptitle in edges:
        key = (sid, oid, plab)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        ecat = category_for_predicate(puri)
        ec = COLORS.get(ecat, COLORS["other"])
        vis_edges.append(
            {
                "id": f"e{ei}",
                "from": sid,
                "to": oid,
                "label": plab,
                "title": f"{ptitle}\n[{ecat}]",
                "color": {"color": ec},
                "arrows": "to",
                "dmfoEdgeCat": ecat,
            }
        )
        ei += 1

    return nodes, vis_edges


def json_embed(data: object) -> str:
    s = json.dumps(data, ensure_ascii=True)
    return s.replace("</script>", "<\\/script>")


def render_html(nodes: list[dict], edges: list[dict], title_suffix: str) -> str:
    cats = [c for c in FILTER_CATEGORY_ORDER if c in COLORS]
    bridge_edges = [
        "bridge_state_identity",
        "bridge_state_activity",
        "bridge_state_evidence",
        "bridge_situation_zone",
        "bridge_situation_regime",
        "bridge_identity_deriv",
    ]
    preset_json = json_embed(
        {
            "all": {"nodes": cats, "edges": cats},
            "anchors_bridges": {
                "label": "Anker + Bridges (A1–A6)",
                "nodes": [
                    "identity_dim", "state_dim", "location_dim",
                    "activity_dim", "context_dim", "evidence_dim",
                    "core_dmfo",
                ],
                "edges": bridge_edges + ["core_dmfo"],
            },
            "identity_state": {
                "label": "Identity & State (A2)",
                "nodes": ["identity_dim", "state_dim", "core_dmfo"],
                "edges": ["bridge_state_identity", "core_dmfo", "state_dim"],
            },
            "evidence": {
                "label": "Evidence (A3)",
                "nodes": ["state_dim", "evidence_dim", "core_dmfo"],
                "edges": ["bridge_state_evidence", "evidence_dim"],
            },
            "context": {
                "label": "Situation & Regime (A4)",
                "nodes": ["context_dim", "core_dmfo"],
                "edges": ["bridge_situation_regime", "context_dim"],
            },
            "activity": {
                "label": "State & Activity (A5)",
                "nodes": ["activity_dim", "state_dim", "provenance", "core_dmfo"],
                "edges": ["bridge_state_activity", "activity_dim", "provenance"],
            },
            "spatial": {
                "label": "Situation & Zone (A6)",
                "nodes": ["context_dim", "location_dim", "core_dmfo"],
                "edges": ["bridge_situation_zone", "location_dim"],
            },
            "identity_deriv": {
                "label": "Identity-Derivation (Split/Merge)",
                "nodes": ["identity_dim", "bridge_identity_deriv", "core_dmfo"],
                "edges": ["bridge_identity_deriv", "core_dmfo", "provenance"],
            },
        }
    )
    nodes_json = json_embed(nodes)
    edges_json = json_embed(edges)
    checkboxes_nodes = "\n".join(
        f'<label class="fcat"><input type="checkbox" class="ncat" value="{c}" checked /> '
        f'<span class="sw" style="background:{COLORS[c]}"></span>'
        f"{CATEGORY_LABELS_DE.get(c, c)}</label>"
        for c in cats
    )
    checkboxes_edges = "\n".join(
        f'<label class="fcat"><input type="checkbox" class="ecat" value="{c}" checked /> '
        f'<span class="sw" style="background:{COLORS[c]}"></span>'
        f"{CATEGORY_LABELS_DE.get(c, c)}</label>"
        for c in cats
    )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <title>DMFO ABox – {title_suffix}</title>
  <script src="{VIS_NETWORK_CDN}"></script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: system-ui, sans-serif; background: #1a1a1e; color: #e8e8ec; }}
    #panel {{
      position: fixed; top: 0; left: 0; width: 320px; max-height: 100vh; overflow-y: auto;
      background: #2d3436; padding: 12px 14px; z-index: 10;
      box-shadow: 4px 0 20px rgba(0,0,0,0.35);
    }}
    #panel h2 {{ margin: 0 0 4px; font-size: 15px; }}
    #panel .sub {{ font-size: 11px; opacity: 0.7; margin-bottom: 10px; }}
    #panel h3 {{ margin: 14px 0 6px; font-size: 12px; text-transform: uppercase; opacity: 0.85; }}
    .fcat {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; font-size: 12px; cursor: pointer; }}
    .sw {{ width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }}
    #presets {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }}
    #presets button {{
      font-size: 11px; padding: 6px 8px; border: none; border-radius: 6px;
      background: #636e72; color: #fff; cursor: pointer;
    }}
    #presets button:hover {{ background: #74b9ff; color: #1a1a1e; }}
    #net {{
      margin-left: 320px; width: calc(100% - 320px); height: 100vh;
      background: #1a1a1e;
    }}
    .hint {{ font-size: 11px; opacity: 0.75; margin-top: 8px; line-height: 1.4; }}
  </style>
</head>
<body>
  <div id="panel">
    <h2>DMFO ABox – Filter</h2>
    <div class="sub">{title_suffix}</div>
    <div id="presets"></div>
    <h3>Knoten-Kategorien</h3>
    <div id="node-filters">{checkboxes_nodes}</div>
    <h3>Kanten-Kategorien</h3>
    <div id="edge-filters">{checkboxes_edges}</div>
    <p class="hint">Kanten erscheinen nur, wenn beide Endknoten sichtbar sind und die Kanten-Kategorie aktiv ist. Die sechs „Bridge"-Kategorien entsprechen den Alignment-Axiomen A2–A6 plus der Identity-Derivation aus §3.3 des Papers.</p>
  </div>
  <div id="net"></div>
  <script>
    const ALL_NODES = {nodes_json};
    const ALL_EDGES = {edges_json};
    const PRESETS = {preset_json};

    const container = document.getElementById("net");
    const nodesDS = new vis.DataSet([]);
    const edgesDS = new vis.DataSet([]);
    const data = {{ nodes: nodesDS, edges: edgesDS }};
    const options = {{
      physics: {{
        enabled: true,
        solver: "forceAtlas2Based",
        forceAtlas2Based: {{
          gravitationalConstant: -38,
          centralGravity: 0.008,
          springLength: 120,
          springConstant: 0.06
        }},
        minVelocity: 0.75
      }},
      edges: {{ arrows: "to", smooth: {{ type: "dynamic" }} }},
      nodes: {{ font: {{ size: 13 }} }},
      interaction: {{ hover: true, tooltipDelay: 80 }}
    }};
    const network = new vis.Network(container, data, options);

    function getChecked(sel) {{
      const s = new Set();
      document.querySelectorAll(sel + ":checked").forEach(cb => s.add(cb.value));
      return s;
    }}

    function applyFilter() {{
      const nodeCats = getChecked(".ncat");
      const edgeCats = getChecked(".ecat");
      const visNodes = ALL_NODES.filter(n => nodeCats.has(n.dmfoNodeCat));
      const idSet = new Set(visNodes.map(n => n.id));
      const visEdges = ALL_EDGES.filter(e =>
        edgeCats.has(e.dmfoEdgeCat) && idSet.has(e.from) && idSet.has(e.to)
      );
      nodesDS.clear();
      edgesDS.clear();
      nodesDS.add(visNodes);
      edgesDS.add(visEdges);
    }}

    document.querySelectorAll(".ncat, .ecat").forEach(cb =>
      cb.addEventListener("change", applyFilter)
    );

    const presetBar = document.getElementById("presets");
    const btnAll = document.createElement("button");
    btnAll.textContent = "Alle an";
    btnAll.onclick = () => {{
      document.querySelectorAll(".ncat, .ecat").forEach(c => {{ c.checked = true; }});
      applyFilter();
    }};
    presetBar.appendChild(btnAll);

    Object.keys(PRESETS).forEach(key => {{
      if (key === "all") return;
      const p = PRESETS[key];
      const b = document.createElement("button");
      b.textContent = p.label || key;
      b.onclick = () => {{
        const nc = new Set(p.nodes);
        const ec = new Set(p.edges);
        document.querySelectorAll(".ncat").forEach(c => {{ c.checked = nc.has(c.value); }});
        document.querySelectorAll(".ecat").forEach(c => {{ c.checked = ec.has(c.value); }});
        applyFilter();
      }};
      presetBar.appendChild(b);
    }});

    applyFilter();
  </script>
</body>
</html>
"""


def render_profile(
    profile: str,
    *,
    output: Path | None,
    include_literals: bool,
    max_edges: int | None,
    abox_only: bool,
) -> Path:
    spec = PROFILES[profile]
    files = spec["abox_only"] if abox_only else spec["files"]
    g = rdflib.Graph()
    for f in files:
        if not f.is_file():
            print(f"WARNUNG: Datei fehlt, übersprungen: {f}", file=sys.stderr)
            continue
        g.parse(str(f), format="turtle")

    labels_by_id = load_labels(g)
    types_map = types_by_node_id(g)

    # Restrict edges to subjects in the profile-example namespace so the
    # graph shows only the ABox individuals (TBox is loaded for type
    # propagation but its axiom-level triples are visually noisy).
    subject_prefixes = [spec["subject_filter"]]

    edges, lit_labels = collect_edges(
        g,
        include_literals=include_literals,
        subject_prefixes=subject_prefixes,
    )
    labels_by_id.update(lit_labels)

    if max_edges is not None and len(edges) > max_edges:
        print(
            f"WARNUNG: {len(edges)} Kanten, schneide auf --max-edges {max_edges} ab.",
            file=sys.stderr,
        )
        edges = edges[:max_edges]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = output if output else OUTPUT_DIR / f"abox_{profile}_{date.today()}.html"
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    nodes, vis_edges = build_vis_data(edges, labels_by_id, types_map)
    html = render_html(nodes, vis_edges, title_suffix=spec["label"])
    out.write_text(html, encoding="utf-8")

    print(f"[{profile}] Triple im Graph: {len(g)}")
    print(f"[{profile}] Knoten: {len(nodes)}, Kanten: {len(vis_edges)}")
    print(f"[{profile}] HTML: {out}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rendert die DMFO-Profil-ABoxes als interaktiven HTML-Graphen "
                    "(vis.js, Slot-/Bridge-farbcodiert, Filter im Browser)."
    )
    parser.add_argument(
        "--profile",
        choices=["maritime", "food", "both"],
        default="both",
        help="Welches Profil visualisieren (default: both).",
    )
    parser.add_argument(
        "--abox",
        type=Path,
        default=None,
        help="Eigene Turtle-Datei statt der Profile (überschreibt --profile).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Ausgabe-HTML (nur sinnvoll mit --abox oder einzelnem --profile).",
    )
    parser.add_argument("--include-literals", action="store_true")
    parser.add_argument("--max-edges", type=int, default=None, metavar="N")
    parser.add_argument(
        "--abox-only",
        action="store_true",
        help="Nur die ABox-Datei laden (ohne TBox-Module — Knoten erscheinen "
             "dann ohne Slot-Klassifikation).",
    )
    args = parser.parse_args()

    if args.abox:
        if not args.abox.is_file():
            print(f"FEHLER: ABox nicht gefunden: {args.abox}", file=sys.stderr)
            return 1
        # Custom-ABox-Modus: nur die übergebene Datei, neutraler Subject-Filter.
        g = rdflib.Graph()
        g.parse(str(args.abox), format="turtle")
        labels_by_id = load_labels(g)
        types_map = types_by_node_id(g)
        edges, lit_labels = collect_edges(
            g, include_literals=args.include_literals, subject_prefixes=None
        )
        labels_by_id.update(lit_labels)
        if args.max_edges and len(edges) > args.max_edges:
            edges = edges[: args.max_edges]
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out = (
            args.output.resolve()
            if args.output
            else (OUTPUT_DIR / f"abox_custom_{date.today()}.html").resolve()
        )
        nodes, vis_edges = build_vis_data(edges, labels_by_id, types_map)
        html = render_html(nodes, vis_edges, title_suffix=str(args.abox))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"Triples: {len(g)} | Knoten: {len(nodes)} | Kanten: {len(vis_edges)}")
        print(f"HTML: {out}")
        return 0

    if args.profile == "both":
        if args.output:
            print(
                "WARNUNG: --output wird ignoriert, wenn --profile=both. "
                "Es entstehen zwei Default-Pfade.",
                file=sys.stderr,
            )
        for prof in ("maritime", "food"):
            render_profile(
                prof,
                output=None,
                include_literals=args.include_literals,
                max_edges=args.max_edges,
                abox_only=args.abox_only,
            )
    else:
        render_profile(
            args.profile,
            output=args.output,
            include_literals=args.include_literals,
            max_edges=args.max_edges,
            abox_only=args.abox_only,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
