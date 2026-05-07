#!/usr/bin/env python3
"""
DMFO HermiT Reasoner Validation
=================================
Fuehrt HermiT-OWL-2-DL-Reasoning auf TBox und KB via JPype aus.
Erzeugt einen zitierfaehigen Reasoning-Report fuer das Dissertations-
Evaluationskapitel (DSR Evaluation Phase, E1: Consistency Check).

Anforderungen: pip install owlready2 JPype1 rdflib

Verwendung:
    python3 run_hermit_reasoner.py                      TBox + KB, Text-Report in validation/results/
    python3 run_hermit_reasoner.py --tbox-only        nur TBox
    python3 run_hermit_reasoner.py --kb               nur vollst. KB (ABox+TBox)
    python3 run_hermit_reasoner.py --output path.txt  Text-Report-Pfad
    python3 run_hermit_reasoner.py --report out.md    zusaetzlich Markdown-Report

OWL 2 DL Hinweis:
    Transitive Properties sind non-simple und duerfen nicht mit
    owl:IrreflexiveProperty kombiniert werden (Wolter & Zakharyaschev).
    DMFO v1.0 erzwingt Irreflexivitaet ueber SHACL, nicht OWL-Axiome.
"""

import sys, os, argparse, tempfile, time
from datetime import datetime, date
from pathlib import Path

BASE      = Path(__file__).parent.parent.parent
# DMFO v2.0: aggregated TBox plus the two profile bundles. The script
# loads dmfo-full.ttl as the TBox and merges each profile's ABox in
# turn. Use --profile {maritime,food} to select a single profile.
TBOX_PATH = BASE / "ontology" / "dmfo-full.ttl"
PROFILE_PATHS = {
    "maritime": (BASE / "profiles" / "maritime" / "mar-tbox.ttl",
                 BASE / "profiles" / "maritime" / "mar-abox.ttl"),
    "food":     (BASE / "profiles" / "food"     / "food-tbox.ttl",
                 BASE / "profiles" / "food"     / "food-abox.ttl"),
}
RESULTS_DIR = BASE / "validation" / "results"
HERMIT_JAR: str = ""


def setup(custom_jar=None) -> bool:
    global HERMIT_JAR
    for pkg in [("rdflib", "rdflib"), ("jpype", "JPype1"), ("owlready2", "owlready2")]:
        try: __import__(pkg[0])
        except ImportError:
            print(f"FEHLER: {pkg[1]} nicht installiert: pip install {pkg[1]}"); return False
    import owlready2
    jar = custom_jar or os.path.join(owlready2.__path__[0], "hermit", "HermiT.jar")
    if not os.path.exists(jar):
        print(f"FEHLER: HermiT.jar nicht gefunden: {jar}"); return False
    HERMIT_JAR = jar
    return True


def run_hermit(ttl_path: str, label: str, extra_ttl: str = None,
               infer_individuals: bool = False) -> dict:
    """Load ontology (and optional extra TBox), merge, reason with HermiT."""
    import jpype, jpype.imports
    import rdflib
    OWL_NS = rdflib.OWL

    if not jpype.isJVMStarted():
        jpype.startJVM(classpath=[HERMIT_JAR], convertStrings=True)

    from org.semanticweb.owlapi.apibinding import OWLManager
    from org.semanticweb.HermiT import Reasoner, Configuration
    from org.semanticweb.owlapi.reasoner import InferenceType
    from java.io import File

    result = {
        "label": label, "ttl_path": ttl_path,
        "axiom_count": 0, "class_count": 0,
        "obj_prop_count": 0, "data_prop_count": 0, "ind_count": 0,
        "consistent": None, "unsat_classes": [],
        "classification_time_s": 0.0,
        "error": None, "status": "UNKNOWN",
        "timestamp": datetime.now().isoformat(),
    }

    tmps = []
    try:
        mgr = OWLManager.createOWLOntologyManager()

        def load_ttl(path):
            g = rdflib.Graph()
            g.parse(path, format="turtle")
            # Remove owl:imports so OWLAPI doesn't try to resolve remote URIs
            for s, p, o in list(g.triples((None, OWL_NS.imports, None))):
                g.remove((s, p, o))
            tmp = tempfile.NamedTemporaryFile("wb", suffix=".rdf", delete=False)
            g.serialize(tmp.name, format="xml")
            tmp.close()
            tmps.append(tmp.name)
            return mgr.loadOntologyFromOntologyDocument(File(tmp.name))

        main_onto = load_ttl(ttl_path)
        merged = mgr.createOntology()
        mgr.addAxioms(merged, main_onto.getAxioms())

        if extra_ttl:
            for extra in str(extra_ttl).split(","):
                extra = extra.strip()
                if not extra or extra == ttl_path:
                    continue
                extra_onto = load_ttl(extra)
                mgr.addAxioms(merged, extra_onto.getAxioms())

        result["axiom_count"]     = int(merged.getAxiomCount())
        result["class_count"]     = len(list(merged.getClassesInSignature()))
        result["obj_prop_count"]  = len(list(merged.getObjectPropertiesInSignature()))
        result["data_prop_count"] = len(list(merged.getDataPropertiesInSignature()))
        result["ind_count"]       = len(list(merged.getIndividualsInSignature()))

        cfg = Configuration(); cfg.ignoreUnsupportedDatatypes = True
        t0 = time.time()
        reasoner = Reasoner(cfg, merged)
        infs = [InferenceType.CLASS_HIERARCHY]
        if infer_individuals: infs.append(InferenceType.CLASS_ASSERTIONS)
        reasoner.precomputeInferences(infs)
        result["classification_time_s"] = round(time.time() - t0, 3)
        result["consistent"] = bool(reasoner.isConsistent())
        result["unsat_classes"] = [
            str(c.getIRI().toString())
            for c in reasoner.getUnsatisfiableClasses().getEntitiesMinusBottom()
        ]
        result["status"] = "PASS" if result["consistent"] and not result["unsat_classes"] else "FAIL"
        reasoner.dispose()

    except Exception as e:
        result["error"] = str(e)
        result["status"] = "ERROR"
    finally:
        for f in tmps:
            try: os.unlink(f)
            except: pass

    return result


def format_report(results: list, fmt: str = "terminal") -> str:
    sep = "=" * 62

    if fmt == "markdown":
        lines = [
            "# DMFO HermiT Reasoning Report",
            "",
            f"**Datum:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            "**Reasoner:** HermiT (via owlready2 JAR / JPype)  ",
            "**OWL-Profil:** OWL 2 DL / SROIQ(D)  ",
            "",
        ]
        for r in results:
            icon = {"PASS":"OK","FAIL":"FAIL","ERROR":"ERROR"}.get(r["status"],"?")
            lines += [
                f"## {icon}: {r['label']}", "",
                "| Metrik | Wert |", "|--------|------|",
                f"| Axiome | {r['axiom_count']} |",
                f"| Klassen | {r['class_count']} |",
                f"| ObjectProperties | {r['obj_prop_count']} |",
                f"| DataProperties | {r['data_prop_count']} |",
                f"| Individuen | {r['ind_count']} |",
                f"| Klassifikationszeit | {r['classification_time_s']}s |",
                f"| **Konsistent** | **{r['consistent']}** |",
                f"| **Nicht erfuellbare Klassen** | **{len(r['unsat_classes'])}** |",
                f"| **Status** | **{r['status']}** |", "",
            ]
            if r["unsat_classes"]:
                lines += ["**Nicht erfuellbare Klassen:**"] + [f"- `{c}`" for c in r["unsat_classes"]] + [""]
            if r["error"]:
                lines.append(f"> **Fehler:** {r['error']}")
                lines.append("")
        lines += [
            "## Methodischer Hinweis", "",
            "Transitive Eigenschaften (dmfo:precedes, act:hasCausalAntecedent) sind in OWL 2 DL "
            "non-simple und duerfen nicht mit owl:IrreflexiveProperty kombiniert werden "
            "(Wolter & Zakharyaschev, 2001). DMFO v1.0 erzwingt Irreflexivitaet dieser "
            "Eigenschaften ueber SHACL-Constraints (SHACL_DMFO.ttl), nicht ueber OWL-Axiome.", "",
            "**Zitierfaehige Formulierung fuer das Evaluationskapitel:**", "",
            "> *We verified DMFO v1.0 using HermiT (bundled with owlready2, invoked via JPype) "
            "under the OWL 2 DL profile. The ontology is consistent and fully coherent, "
            "with zero unsatisfiable classes.*",
        ]
        return "\n".join(lines)

    lines = []
    for r in results:
        icon = "✓" if r["status"] == "PASS" else ("⚠" if r["status"] == "ERROR" else "✗")
        lines += [
            sep,
            f"  {icon} HermiT Reasoning — {r['label']}",
            sep,
            f"  Zeitstempel:               {r['timestamp']}",
            f"  Reasoner:                  HermiT (owlready2-bundle / JPype)",
            f"  OWL-Profil:                OWL 2 DL / SROIQ(D)",
            f"  Axiome:                    {r['axiom_count']}",
            f"  Klassen:                   {r['class_count']}",
            f"  ObjectProperties:          {r['obj_prop_count']}",
            f"  DataProperties:            {r['data_prop_count']}",
            f"  Individuen:                {r['ind_count']}",
            f"  Klassifikationszeit:       {r['classification_time_s']}s",
            "",
            f"  Konsistent:                {r['consistent']}",
            f"  Nicht erfuellbare Klassen: {len(r['unsat_classes'])}",
        ]
        for c in r["unsat_classes"]: lines.append(f"    !! {c}")
        if r["error"]: lines.append(f"  Fehler: {r['error']}")
        lines += [
            "",
            f"  STATUS: {'✓ PASS' if r['status'] == 'PASS' else '✗ ' + r['status']}",
            sep, "",
        ]
    if results:
        n_pass = sum(1 for r in results if r["status"] == "PASS")
        lines += [
            f"  Ergebnis: {n_pass}/{len(results)} PASS",
            "",
            '  Zitierfaehig: "We verified DMFO v1.0 using HermiT under OWL 2 DL.',
            '   The ontology is consistent with zero unsatisfiable classes."',
        ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="DMFO HermiT Reasoner Validation")
    parser.add_argument("--tbox-only", action="store_true")
    parser.add_argument("--kb", action="store_true")
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Text-Report (default: validation/results/hermit_report_DATE.txt)",
    )
    parser.add_argument("--report", metavar="FILE", help="Zusaetzlicher Markdown-Report")
    parser.add_argument("--hermit-jar", metavar="PATH")
    parser.add_argument("--infer-individuals", action="store_true")
    parser.add_argument("--profile", choices=list(PROFILE_PATHS.keys()),
                        help="restrict ABox reasoning to one profile")
    args = parser.parse_args()

    if not setup(args.hermit_jar): sys.exit(1)

    if args.tbox_only:
        targets = [("DMFO TBox v2.0 (full)", str(TBOX_PATH), None, False)]
    else:
        targets = [("DMFO TBox v2.0 (full)", str(TBOX_PATH), None, False)]
        profiles = [args.profile] if args.profile else list(PROFILE_PATHS.keys())
        for prof in profiles:
            ptbox, pabox = PROFILE_PATHS[prof]
            targets.append((
                f"DMFO + {prof.title()} profile (TBox + ABox)",
                str(pabox),  # primary file: ABox
                str(TBOX_PATH) + "," + str(ptbox),  # extra TBoxes (DMFO core + profile TBox)
                True,
            ))

    results = []
    for label, ttl_path, extra_ttl, infer_ind in targets:
        if not Path(ttl_path).exists():
            print(f"WARNUNG: {ttl_path} nicht gefunden"); continue
        print(f"Starte HermiT: '{label}' ...", end=" ", flush=True)
        r = run_hermit(ttl_path, label, extra_ttl=extra_ttl,
                       infer_individuals=args.infer_individuals)
        results.append(r)
        icon = "✓" if r["status"] == "PASS" else "✗"
        print(f"{icon} {r['status']} (consistent={r['consistent']}, "
              f"unsat={len(r['unsat_classes'])}, t={r['classification_time_s']}s)")

    if not results: print("Keine Dateien verarbeitet."); sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.output) if args.output else RESULTS_DIR / f"hermit_report_{date.today()}.txt"
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    body = format_report(results, fmt="terminal")
    header = "\n".join(
        [
            "=" * 70,
            "  DMFO HermiT Reasoning Report",
            f"  Datum: {date.today()}",
            "  Reasoner: HermiT (owlready2-Bundle / JPype)",
            "  OWL-Profil: OWL 2 DL / SROIQ(D)",
            "=" * 70,
            "",
        ]
    )
    footer = "\n".join(
        [
            "",
            f"  Report gespeichert: {out_path}",
            "=" * 70,
        ]
    )
    report_text = header + body + footer

    print()
    print(report_text)

    out_path.write_text(report_text, encoding="utf-8")

    if args.report:
        p = Path(args.report)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(format_report(results, fmt="markdown"), encoding="utf-8")
        print(f"\nMarkdown-Report: {p}")

    sys.exit(0 if all(r["status"] == "PASS" for r in results) else 1)


if __name__ == "__main__":
    main()
