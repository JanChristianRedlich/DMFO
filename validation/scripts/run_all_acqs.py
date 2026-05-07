#!/usr/bin/env python3
"""
DMFO ACQ Runner
===============

Executes the 20 Anchor Competence Questions (ACQ-I-* through ACQ-IV-*)
against either of the two DMFO-conformant profiles. With --b1, runs the
same queries against an ablated KB (DMFO − A1–A6) and produces the
ablation comparison reported in Paper §4.2 / Table 3.

Usage:
    python3 run_all_acqs.py --profile maritime
    python3 run_all_acqs.py --profile food
    python3 run_all_acqs.py --profile maritime --b1
    python3 run_all_acqs.py --all   # both profiles, with B1 comparison

Outputs:
    validation/results/queries_<profile>.json
    validation/results/ablation_<profile>.json   (when --b1 or --all)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

try:
    from rdflib import Graph, RDF, RDFS, OWL, URIRef
    import owlrl
except ImportError:  # pragma: no cover
    sys.stderr.write("ERROR: rdflib + owlrl required.\n")
    sys.exit(2)


# Documentation predicates — not load-bearing for any ACQ; stripped
# from the runtime KB to reduce closure-expansion cost. Same strip is
# applied symmetrically to the B2-CCO baseline runner so the timing
# comparison is apples-to-apples.
_DOC_PREDS = {RDFS.label, RDFS.comment, RDFS.isDefinedBy, RDFS.seeAlso,
              URIRef('http://www.w3.org/2004/02/skos/core#scopeNote'),
              URIRef('http://www.w3.org/2004/02/skos/core#closeMatch'),
              URIRef('http://www.w3.org/2004/02/skos/core#exactMatch')}
_DOC_PFX = ('http://purl.org/dc/terms/', 'http://purl.org/vocab/vann/')


def _strip_runtime_metadata(g: Graph) -> int:
    """Remove documentation triples whose subject is a TBox node
    (owl:Class, owl:ObjectProperty, owl:DatatypeProperty,
    owl:AnnotationProperty, owl:Ontology). ABox individuals' labels /
    comments are preserved because some baseline patterns (e.g. CCO's
    ICE-mediated identifier model) carry semantic content on
    rdfs:label of instances. Returns count of triples removed."""
    n = 0
    # 1. owl:Ontology header triples
    for s in list(g.subjects(RDF.type, OWL.Ontology)):
        for s2, p, o in list(g.triples((s, None, None))):
            g.remove((s2, p, o)); n += 1
    # 2. Find TBox subjects (Class / ObjectProperty / DatatypeProperty /
    #    AnnotationProperty)
    tbox_types = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty,
                  OWL.AnnotationProperty, OWL.FunctionalProperty,
                  OWL.InverseFunctionalProperty, OWL.SymmetricProperty,
                  OWL.TransitiveProperty, OWL.IrreflexiveProperty,
                  RDFS.Class}
    tbox_subjects = set()
    for t in tbox_types:
        tbox_subjects.update(g.subjects(RDF.type, t))
    # 3. Strip doc triples on TBox subjects only
    for s in tbox_subjects:
        for s2, p, o in list(g.triples((s, None, None))):
            if p in _DOC_PREDS or any(str(p).startswith(pfx) for pfx in _DOC_PFX):
                g.remove((s2, p, o)); n += 1
    # 4. Strip dcterms/vann annotations everywhere (these are pure metadata
    #    on ontology-level subjects and rarely on ABox individuals)
    for s, p, o in list(g):
        if any(str(p).startswith(pfx) for pfx in _DOC_PFX):
            g.remove((s, p, o)); n += 1
    return n


def _expand_with_rdfs_owl(g: Graph) -> Graph:
    """Apply OWL-RL deductive closure (default) so the ACQ catalogue
    exercises sub-property and sub-class entailments expected by
    Paper §3.2 / §4.2. (A1)–(A6) are stated as subPropertyOf /
    domain / range axioms — closure must be materialised before the
    queries run.

    Runtime knobs (env vars):
      DMFO_RUNTIME_STRIP=1 (default) — strip documentation triples on
        TBox subjects + owl:Ontology headers before closure. ABox
        rdfs:label is preserved.
      DMFO_CLOSURE=owl-rl (default) | rdfs | rdfs+rl | none —
        closure-strategy override. RDFS_Semantics is sufficient for
        the 20-ACQ catalogue (verified by
        validation/scripts/perf-rdfs-symmetric.py); OWL-RL is the
        conservative default consistent with Paper §3 P1."""
    import os
    if os.environ.get('DMFO_RUNTIME_STRIP', '1') != '0':
        _strip_runtime_metadata(g)
    strategy = os.environ.get('DMFO_CLOSURE', 'owl-rl').lower()
    if strategy == 'none':
        return g
    if strategy == 'rdfs':
        owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(g)
    elif strategy == 'rdfs+rl':
        owlrl.DeductiveClosure(owlrl.RDFS_OWLRL_Semantics).expand(g)
    else:  # owl-rl, default
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = REPO_ROOT / "ontology"
PROFILES_DIR = REPO_ROOT / "profiles"
ACQ_DIR = REPO_ROOT / "acqs" / "queries" / "dmfo"
RESULTS_DIR = REPO_ROOT / "validation" / "results"

ACQ_FILE_RE = re.compile(r"^ACQ-(I|II|III|IV)-(\d+)_(.+)\.sparql$")

# Axiom triples to strip when --b1 is requested. These match the patterns
# checked by acqs/queries/conformance/A?.ask.rq.
B1_STRIP_PATTERNS = [
    # A2: domain/range on dmfo:manifestationOf
    ("https://w3id.org/dmfo#manifestationOf",
     "http://www.w3.org/2000/01/rdf-schema#domain", None),
    ("https://w3id.org/dmfo#manifestationOf",
     "http://www.w3.org/2000/01/rdf-schema#range", None),
    # A4: domain/range on dmfo:governedBy
    ("https://w3id.org/dmfo#governedBy",
     "http://www.w3.org/2000/01/rdf-schema#domain", None),
    ("https://w3id.org/dmfo#governedBy",
     "http://www.w3.org/2000/01/rdf-schema#range", None),
    # A5: subPropertyOf prov:wasGeneratedBy + domain/range
    ("https://w3id.org/dmfo#stateWasGeneratedBy",
     "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
     "http://www.w3.org/ns/prov#wasGeneratedBy"),
    ("https://w3id.org/dmfo#stateWasGeneratedBy",
     "http://www.w3.org/2000/01/rdf-schema#domain", None),
    ("https://w3id.org/dmfo#stateWasGeneratedBy",
     "http://www.w3.org/2000/01/rdf-schema#range", None),
    # A6: subPropertyOf geo:sfWithin + domain/range
    ("https://w3id.org/dmfo#situatedAt",
     "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
     "http://www.opengis.net/ont/geosparql#sfWithin"),
    ("https://w3id.org/dmfo#situatedAt",
     "http://www.w3.org/2000/01/rdf-schema#domain", None),
    ("https://w3id.org/dmfo#situatedAt",
     "http://www.w3.org/2000/01/rdf-schema#range", None),
]


@dataclass
class ACQ:
    cls: str          # "I" / "II" / "III" / "IV"
    idx: str
    name: str
    path: Path

    @property
    def full_id(self) -> str:
        return f"ACQ-{self.cls}-{self.idx}"


def discover_acqs() -> list[ACQ]:
    items: list[ACQ] = []
    for f in sorted(ACQ_DIR.glob("ACQ-*.sparql")):
        m = ACQ_FILE_RE.match(f.name)
        if not m:
            continue
        items.append(ACQ(cls=m.group(1), idx=m.group(2), name=m.group(3), path=f))
    return items


def load_kb(profile: str, materialise: bool = True) -> Graph:
    g = Graph()
    for f in ONTOLOGY_DIR.glob("dmfo-*.ttl"):
        g.parse(str(f), format="turtle")
    profile_dir = PROFILES_DIR / profile
    for f in profile_dir.glob("*-tbox.ttl"):
        g.parse(str(f), format="turtle")
    for f in profile_dir.glob("*-abox.ttl"):
        g.parse(str(f), format="turtle")
    if materialise:
        _expand_with_rdfs_owl(g)
    return g


def strip_a1_a6(graph: Graph) -> Graph:
    """Build a B1 KB from a DMFO-conformant graph.

    Per Paper §4.2 ("B1 is identical to DMFO modulo (A1)–(A6)"), the B1
    profile imports the same anchor vocabularies and the same ABox
    population but fails the alignment constraints by construction. We
    realise this in two steps:

      1. Remove the alignment axioms themselves (T-Box).
      2. Down-map the typed bridges in the ABox to their imported
         super-properties, so the ABox is *equivalent in information*
         under PROV-O / SOSA / DUL / GeoSPARQL semantics but no longer
         exposes the typed dmfo:* paths that ACQ queries traverse.

    Step (2) is what makes the ablation bite: under the conformant
    profile, an ACQ that asks ?m dmfo:stateWasGeneratedBy ?a returns a
    binding because (A5) types both the property and its instances in
    the data graph. Under B1, the same information is encoded as
    prov:wasGeneratedBy without the typed dmfo:* hop, so the ACQ —
    which is written against the DMFO bridge — returns empty.
    """
    from rdflib import URIRef, RDFS, OWL, RDF
    out = Graph()
    out += graph

    # ── (1) T-Box: remove alignment axioms ─────────────────────────
    manifestation = URIRef("https://w3id.org/dmfo#Manifestation")
    for restr in list(out.objects(manifestation, RDFS.subClassOf)):
        if (restr, OWL.intersectionOf, None) in out:
            for s, p, o in list(out.triples((restr, None, None))):
                out.remove((s, p, o))
            for s, p, o in list(out.triples((None, None, restr))):
                out.remove((s, p, o))
    for s, p, o in B1_STRIP_PATTERNS:
        sub = URIRef(s); pre = URIRef(p)
        obj = URIRef(o) if o else None
        if obj is None:
            for triple in list(out.triples((sub, pre, None))):
                out.remove(triple)
        else:
            out.remove((sub, pre, obj))
    evidenced = URIRef("https://w3id.org/dmfo#evidencedBy")
    for inv in list(out.objects(evidenced, RDFS.subPropertyOf)):
        if (inv, OWL.inverseOf, None) in out:
            for s, p, o in list(out.triples((inv, None, None))):
                out.remove((s, p, o))
            out.remove((evidenced, RDFS.subPropertyOf, inv))

    # ── (2) ABox: rewrite typed dmfo:* bridges to imported vocab ──
    #
    # Each rewrite preserves the logical information (the conformant
    # profile already entails the imported super-property triple via
    # subPropertyOf, but the dmfo:* hop disappears under B1).
    sosa_hasFOI = URIRef("http://www.w3.org/ns/sosa/hasFeatureOfInterest")
    prov_wasGenBy = URIRef("http://www.w3.org/ns/prov#wasGeneratedBy")
    dul_satisfies = URIRef("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#satisfies")
    geo_sfWithin = URIRef("http://www.opengis.net/ont/geosparql#sfWithin")

    bridge_remaps: list[tuple[URIRef, URIRef, bool]] = [
        # (dmfo:bridge, replacement, swap_subject_object)
        (URIRef("https://w3id.org/dmfo#stateWasGeneratedBy"), prov_wasGenBy, False),
        (URIRef("https://w3id.org/dmfo#governedBy"),          dul_satisfies, False),
        (URIRef("https://w3id.org/dmfo#situatedAt"),              geo_sfWithin,  False),
        (URIRef("https://w3id.org/dmfo#evidencedBy"),         sosa_hasFOI,   True),
    ]
    for dmfo_p, repl, swap in bridge_remaps:
        for s, _, o in list(out.triples((None, dmfo_p, None))):
            out.remove((s, dmfo_p, o))
            if swap:
                out.add((o, repl, s))
            else:
                out.add((s, repl, o))
    return out


def run_acqs(kb: Graph, acqs: list[ACQ]) -> dict:
    results: list[dict] = []
    for acq in acqs:
        text = acq.path.read_text(encoding="utf-8")
        t0 = time.perf_counter()
        try:
            qres = kb.query(text)
            rows = list(qres)
            elapsed = time.perf_counter() - t0
            results.append({
                "id": acq.full_id, "class": acq.cls, "name": acq.name,
                "result_rows": len(rows),
                "answerable": len(rows) > 0,
                "elapsed_s": round(elapsed, 4),
            })
        except Exception as exc:  # pragma: no cover
            elapsed = time.perf_counter() - t0
            results.append({
                "id": acq.full_id, "class": acq.cls, "name": acq.name,
                "result_rows": 0, "answerable": False, "error": str(exc),
                "elapsed_s": round(elapsed, 4),
            })
    return {"acqs": results}


def summarise(report: dict) -> dict:
    by_class: dict[str, dict[str, int]] = {}
    for r in report["acqs"]:
        c = r["class"]
        by_class.setdefault(c, {"total": 0, "answerable": 0})
        by_class[c]["total"] += 1
        if r["answerable"]:
            by_class[c]["answerable"] += 1
    total = sum(c["total"] for c in by_class.values())
    answerable = sum(c["answerable"] for c in by_class.values())
    return {
        "by_class": by_class,
        "total": total, "answerable": answerable,
        "score": f"{answerable}/{total}",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", choices=["maritime", "food"])
    ap.add_argument("--b1", action="store_true",
                    help="also run against B1 ablation (DMFO − A1–A6)")
    ap.add_argument("--all", action="store_true",
                    help="run for both profiles with B1 comparison")
    args = ap.parse_args(argv)

    if not args.profile and not args.all:
        ap.error("--profile or --all is required")

    targets = ["maritime", "food"] if args.all else [args.profile]
    RESULTS_DIR.mkdir(exist_ok=True)
    acqs = discover_acqs()

    overall: dict = {}
    for prof in targets:
        kb = load_kb(prof)
        rep = run_acqs(kb, acqs)
        rep["summary"] = summarise(rep)
        rep["profile"] = prof
        rep["kb_triples"] = len(kb)
        out_path = RESULTS_DIR / f"queries_{prof}.json"
        out_path.write_text(json.dumps(rep, indent=2), encoding="utf-8")
        overall[prof] = {"queries": rep}

        print(f"\n[{prof}] DMFO score: {rep['summary']['score']}  "
              f"by class: " + ", ".join(
                f"{c}={rep['summary']['by_class'][c]['answerable']}/"
                f"{rep['summary']['by_class'][c]['total']}"
                for c in sorted(rep["summary"]["by_class"])))

        if args.b1 or args.all:
            # B1 KB: strip A1–A6 from the *un-materialised* graph and
            # then apply OWL-RL closure, so the absence of the
            # alignment axioms genuinely impacts which entailments
            # become available to the SPARQL engine.
            kb_b1_raw = Graph()
            for f in ONTOLOGY_DIR.glob("dmfo-*.ttl"):
                kb_b1_raw.parse(str(f), format="turtle")
            for f in (PROFILES_DIR / prof).glob("*-tbox.ttl"):
                kb_b1_raw.parse(str(f), format="turtle")
            for f in (PROFILES_DIR / prof).glob("*-abox.ttl"):
                kb_b1_raw.parse(str(f), format="turtle")
            kb_b1 = strip_a1_a6(kb_b1_raw)
            _expand_with_rdfs_owl(kb_b1)
            rep_b1 = run_acqs(kb_b1, acqs)
            rep_b1["summary"] = summarise(rep_b1)
            rep_b1["profile"] = prof
            rep_b1["kb_triples"] = len(kb_b1)
            ablation = {
                "profile": prof,
                "DMFO": rep["summary"],
                "B1":   rep_b1["summary"],
                "delta": {
                    "answerable_diff": rep["summary"]["answerable"] - rep_b1["summary"]["answerable"],
                },
                "per_acq": [
                    {"id": a["id"], "class": a["class"],
                     "DMFO_rows": a["result_rows"],
                     "B1_rows": b["result_rows"]}
                    for a, b in zip(rep["acqs"], rep_b1["acqs"])
                ],
            }
            out_path = RESULTS_DIR / f"ablation_{prof}.json"
            out_path.write_text(json.dumps(ablation, indent=2), encoding="utf-8")
            overall[prof]["ablation"] = ablation
            print(f"[{prof}] B1   score: {rep_b1['summary']['score']}")
            print(f"[{prof}] Δ:           {ablation['delta']['answerable_diff']} ACQs lost without (A1)–(A6)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
