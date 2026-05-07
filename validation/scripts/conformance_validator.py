#!/usr/bin/env python3
"""
DMFO Conformance Validator
==========================

Checks whether a candidate profile (TBox + ABox) is DMFO-conformant in
the sense of Definition 1 of the paper:

    P = (D, B, S) is DMFO-conformant iff
       (i)  P imports the activated anchor and bridge modules,
       (ii) the binding axioms in B satisfy (A1)–(A6) over the anchor
            signature, and
       (iii) its ABoxes validate against S together with the DMFO core
             shapes.

Usage:
    python3 conformance_validator.py profiles/maritime
    python3 conformance_validator.py profiles/food --json

The exit code is 0 iff the profile is conformant.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from rdflib import Graph
    from pyshacl import validate as pyshacl_validate
except ImportError:  # pragma: no cover
    sys.stderr.write("ERROR: rdflib + pyshacl required.\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
ONTOLOGY_DIR = REPO_ROOT / "ontology"
SHAPES_DIR = REPO_ROOT / "shapes"
CONFORMANCE_DIR = REPO_ROOT / "acqs" / "queries" / "conformance"
RESULTS_DIR = REPO_ROOT / "validation" / "results"

ALIGNMENT_AXIOMS = ["A1", "A2", "A3", "A4", "A5", "A6"]


def load_dmfo_tbox() -> Graph:
    g = Graph()
    for f in ONTOLOGY_DIR.glob("dmfo-*.ttl"):
        g.parse(str(f), format="turtle")
    return g


def load_profile(profile_dir: Path) -> tuple[Graph, Graph, Graph]:
    tbox = Graph()
    abox = Graph()
    shapes = Graph()
    for f in profile_dir.glob("*-tbox.ttl"):
        tbox.parse(str(f), format="turtle")
    for f in profile_dir.glob("*-abox.ttl"):
        abox.parse(str(f), format="turtle")
    for f in profile_dir.glob("*-shapes.ttl"):
        shapes.parse(str(f), format="turtle")
    return tbox, abox, shapes


def run_axiom_asks(tbox: Graph) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for axiom_id in ALIGNMENT_AXIOMS:
        ask_path = CONFORMANCE_DIR / f"{axiom_id}.ask.rq"
        query_text = ask_path.read_text(encoding="utf-8")
        ans = bool(tbox.query(query_text).askAnswer)
        results[axiom_id] = ans
    return results


def check_imports(tbox: Graph) -> dict[str, bool]:
    """Verify that the profile TBox owl:imports the DMFO umbrella ontology."""
    from rdflib import OWL, URIRef
    expected = URIRef("https://w3id.org/dmfo")
    imports = list(tbox.objects(predicate=OWL.imports))
    return {
        "imports_dmfo": expected in imports,
        "imports": [str(i) for i in imports],
    }


def check_anchor_bindings(profile_tbox: Graph) -> dict:
    """For every domain class declared as rdfs:subClassOf an anchor, record
    the binding. Each domain class in the State slot must subclass
    dmfo:Manifestation, in Identity must subclass dmfo:TimeVaryingEntity, etc."""
    from rdflib import RDFS, URIRef
    anchors = {
        "TimeVaryingEntity": URIRef("https://w3id.org/dmfo#TimeVaryingEntity"),
        "Manifestation":     URIRef("https://w3id.org/dmfo#Manifestation"),
        "prov:Activity":     URIRef("http://www.w3.org/ns/prov#Activity"),
        "sosa:Observation":  URIRef("http://www.w3.org/ns/sosa/Observation"),
        "dul:Situation":     URIRef("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Situation"),
        "dul:Description":   URIRef("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Description"),
        "geo:Feature":       URIRef("http://www.opengis.net/ont/geosparql#Feature"),
    }
    bindings: dict[str, list[str]] = {k: [] for k in anchors}
    for slot, anchor in anchors.items():
        for s in profile_tbox.subjects(RDFS.subClassOf, anchor):
            bindings[slot].append(str(s))
    bindings["any_binding"] = any(v for v in bindings.values() if isinstance(v, list))  # type: ignore[arg-type]
    return bindings


def run_shacl(profile_tbox: Graph, profile_abox: Graph, profile_shapes: Graph,
              dmfo_tbox: Graph) -> dict:
    data = profile_tbox + profile_abox + dmfo_tbox
    shapes = Graph()
    for shape_file in SHAPES_DIR.glob("*.ttl"):
        shapes.parse(str(shape_file), format="turtle")
    shapes += profile_shapes
    conforms, _, txt = pyshacl_validate(
        data_graph=data,
        shacl_graph=shapes,
        ont_graph=None,
        inference="rdfs",
        debug=False,
    )
    return {"conforms": bool(conforms), "report": txt}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("profile", help="path to profile directory (e.g. profiles/maritime)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-shacl", action="store_true",
                    help="skip the SHACL validation step (faster)")
    args = ap.parse_args(argv)

    profile_path = Path(args.profile).resolve()
    if not profile_path.is_dir():
        sys.stderr.write(f"ERROR: profile path not found: {profile_path}\n")
        return 2

    dmfo_tbox = load_dmfo_tbox()
    p_tbox, p_abox, p_shapes = load_profile(profile_path)

    report: dict = {"profile": str(profile_path.relative_to(REPO_ROOT))}
    report["imports"] = check_imports(p_tbox)

    # Run A1-A6 ASKs against the merged TBox so that imports closure is
    # available to the query engine.
    merged_tbox = dmfo_tbox + p_tbox
    report["axioms"] = run_axiom_asks(merged_tbox)
    report["all_axioms_pass"] = all(report["axioms"].values())

    report["bindings"] = check_anchor_bindings(p_tbox)

    if not args.no_shacl:
        report["shacl"] = run_shacl(p_tbox, p_abox, p_shapes, dmfo_tbox)
    else:
        report["shacl"] = {"skipped": True}

    report["conformant"] = (
        report["imports"]["imports_dmfo"]
        and report["all_axioms_pass"]
        and (report["shacl"].get("conforms") or args.no_shacl)
    )

    RESULTS_DIR.mkdir(exist_ok=True)
    profile_name = profile_path.name
    out_path = RESULTS_DIR / f"conformance_{profile_name}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(f"\nDMFO conformance check — profile: {profile_name}")
        print("─" * 60)
        print(f"  imports DMFO:         {'PASS' if report['imports']['imports_dmfo'] else 'FAIL'}")
        for ax, ok in report["axioms"].items():
            print(f"  ({ax}):                  {'PASS' if ok else 'FAIL'}")
        print(f"  domain bindings:      "
              f"{sum(len(v) for k,v in report['bindings'].items() if isinstance(v, list))} class(es)")
        if not args.no_shacl:
            print(f"  SHACL:                {'PASS' if report['shacl']['conforms'] else 'FAIL'}")
        print(f"\n  CONFORMANT:           {'YES' if report['conformant'] else 'NO'}")
        print(f"  report → {out_path.relative_to(REPO_ROOT)}")
    return 0 if report["conformant"] else 1


if __name__ == "__main__":
    sys.exit(main())
