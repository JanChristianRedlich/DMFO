#!/usr/bin/env python3
"""
DMFO Knowledge Base Validator
=============================

Parses every TTL file in the DMFO module set + profile artefacts,
checks RDF syntax, reports per-file triple counts, and verifies that
no bridge property carries an existential GCI (Paper Theorem 2 / data-
of-opportunity constraint).

Usage:
    python3 validation/scripts/validate_kb.py
    python3 validation/scripts/validate_kb.py --verbose
    python3 validation/scripts/validate_kb.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from rdflib import Graph, Namespace, OWL, RDF, RDFS, URIRef
except ImportError:  # pragma: no cover
    sys.stderr.write("ERROR: rdflib not installed. Run `pip install rdflib`.\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
DMFO = Namespace("https://w3id.org/dmfo#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")

ONTOLOGY_FILES = sorted((REPO_ROOT / "ontology").glob("dmfo-*.ttl"))
PROFILE_FILES = sorted((REPO_ROOT / "profiles").rglob("*.ttl"))
SHAPE_FILES = sorted((REPO_ROOT / "shapes").glob("*.ttl"))

OPTIONAL_BRIDGES = [
    DMFO.evidencedBy,
    DMFO.governedBy,
    DMFO.situatedAt,
    DMFO.stateWasGeneratedBy,
]


def parse(path: Path) -> tuple[Graph | None, str | None]:
    g = Graph()
    try:
        g.parse(str(path), format="turtle")
        return g, None
    except Exception as exc:  # rdflib raises a variety of subclasses
        return None, str(exc)


def has_existential_gci(graph: Graph, prop: URIRef) -> bool:
    """True iff the graph contains owl:Restriction (owl:onProperty prop ; owl:someValuesFrom _ )
    that participates in a class subsumption — i.e. an existential GCI."""
    for restr in graph.subjects(OWL.onProperty, prop):
        if (restr, OWL.someValuesFrom, None) in graph:
            # any class that is rdfs:subClassOf the restriction is GCI-bearing
            for _ in graph.subjects(RDFS.subClassOf, restr):
                return True
            # equivalentClass also entails existential commitment
            for _ in graph.subjects(OWL.equivalentClass, restr):
                return True
    return False


def collect_kb(*paths: Path) -> Graph:
    kb = Graph()
    for p in paths:
        kb.parse(str(p), format="turtle")
    return kb


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="emit JSON report on stdout")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    report: dict = {"files": {}, "syntax_errors": 0, "total_triples": 0,
                    "bridge_gci_violations": [], "summary": {}}

    files = ONTOLOGY_FILES + PROFILE_FILES + SHAPE_FILES
    for f in files:
        rel = f.relative_to(REPO_ROOT)
        g, err = parse(f)
        if err is not None:
            report["files"][str(rel)] = {"ok": False, "error": err, "triples": 0}
            report["syntax_errors"] += 1
            if not args.json:
                print(f"  FAIL  {rel}: {err}")
        else:
            n = len(g)
            report["files"][str(rel)] = {"ok": True, "triples": n}
            report["total_triples"] += n
            if not args.json and args.verbose:
                print(f"  OK    {rel}: {n} triples")

    # Bridge GCI check on the merged TBox closure
    try:
        merged = collect_kb(*ONTOLOGY_FILES)
        for prop in OPTIONAL_BRIDGES:
            if has_existential_gci(merged, prop):
                report["bridge_gci_violations"].append(str(prop))
    except Exception as exc:
        report["bridge_gci_violations"].append(f"merge-failed: {exc}")

    report["summary"] = {
        "n_files": len(files),
        "n_ok": sum(1 for v in report["files"].values() if v.get("ok")),
        "n_failed": report["syntax_errors"],
        "n_bridge_gcis": len(report["bridge_gci_violations"]),
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["syntax_errors"] == 0 and not report["bridge_gci_violations"] else 1

    summ = report["summary"]
    print()
    print("DMFO KB validation report")
    print("─" * 60)
    print(f"  Files parsed:          {summ['n_ok']} / {summ['n_files']}")
    print(f"  Total triples:         {report['total_triples']}")
    print(f"  Syntax errors:         {summ['n_failed']}")
    print(f"  Bridge GCI violations: {summ['n_bridge_gcis']}")
    if report["bridge_gci_violations"]:
        for v in report["bridge_gci_violations"]:
            print(f"    - {v}")
    print()
    return 0 if summ["n_failed"] == 0 and summ["n_bridge_gcis"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
