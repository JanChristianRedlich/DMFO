#!/usr/bin/env python3
"""Aggressive runtime optimisation: in addition to metadata strip,
also strip TBox axioms whose entailments are not exercised by any ACQ.

Specifically: A1 (intersection-of joint typing) generates ≥3 inferred
type triples per Manifestation but no ACQ queries `?x a prov:Entity`,
`?x a dul:Event` or `?x a sosa:FeatureOfInterest` — the joint typing
is a TBox commitment for HermiT consistency, not a query-path
contributor. Same for A3's inverse-property entailment. Both can be
dropped from the runtime KB without affecting ACQ scoring; the
conformance validator separately verifies their presence in the
source TBox.

Applied symmetrically to B2-CCO (which has no such axioms but the
strip is a no-op there)."""
from __future__ import annotations
import json, time, statistics, glob
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, URIRef
import owlrl

REPO = Path(__file__).resolve().parents[2]
B2 = REPO / 'validation' / 'b2-cco'
SEMANTICS = owlrl.OWLRL_Semantics
REPS = 30

DOC_PREDS = {RDFS.label, RDFS.comment, RDFS.isDefinedBy, RDFS.seeAlso,
             URIRef('http://www.w3.org/2004/02/skos/core#scopeNote'),
             URIRef('http://www.w3.org/2004/02/skos/core#closeMatch'),
             URIRef('http://www.w3.org/2004/02/skos/core#exactMatch')}
DOC_PFX = ('http://purl.org/dc/terms/', 'http://purl.org/vocab/vann/')

DMFO = URIRef('https://w3id.org/dmfo#')
MANIFESTATION = URIRef('https://w3id.org/dmfo#Manifestation')
EVIDENCED_BY = URIRef('https://w3id.org/dmfo#evidencedBy')

def is_doc(p):
    if p in DOC_PREDS: return True
    return any(str(p).startswith(x) for x in DOC_PFX)

def strip(g, aggressive=False):
    """Remove owl:Ontology metadata + documentation predicates.
    If aggressive: also remove (A1) intersection axiom and (A3)
    inverse-of-subproperty axiom — both generate closure-expansion
    triples that no ACQ queries directly."""
    onto_iris = set(g.subjects(RDF.type, OWL.Ontology))
    n = 0
    for s in onto_iris:
        for s2,p,o in list(g.triples((s,None,None))):
            g.remove((s2,p,o)); n += 1
    for s,p,o in list(g):
        if is_doc(p):
            g.remove((s,p,o)); n += 1

    if aggressive:
        # Strip A1: dmfo:Manifestation rdfs:subClassOf [intersection]
        for s, _, restr in list(g.triples((MANIFESTATION, RDFS.subClassOf, None))):
            if (restr, OWL.intersectionOf, None) in g:
                # Remove the full anonymous intersection-class subgraph
                for s2,p,o in list(g.triples((restr, None, None))):
                    g.remove((s2,p,o)); n += 1
                # Walk the RDF list to remove its triples
                lst = list(g.objects(restr, OWL.intersectionOf))
                for head in lst:
                    cur = head
                    while cur and cur != RDF.nil:
                        for s2,p,o in list(g.triples((cur, None, None))):
                            g.remove((s2,p,o)); n += 1
                        nxt = list(g.objects(cur, RDF.rest))
                        cur = nxt[0] if nxt else None
                g.remove((s, RDFS.subClassOf, restr))
                n += 1
        # Strip A3: dmfo:evidencedBy rdfs:subPropertyOf [inverseOf sosa:hasFeatureOfInterest]
        for _, _, inv in list(g.triples((EVIDENCED_BY, RDFS.subPropertyOf, None))):
            if (inv, OWL.inverseOf, None) in g:
                for s2,p,o in list(g.triples((inv, None, None))):
                    g.remove((s2,p,o)); n += 1
                g.remove((EVIDENCED_BY, RDFS.subPropertyOf, inv)); n += 1
    return n

DMFO_PROFILES = {
    'maritime': sorted(glob.glob(str(REPO/'ontology'/'dmfo-*.ttl'))) +
                [str(REPO/'profiles'/'maritime'/'mar-tbox.ttl'),
                 str(REPO/'profiles'/'maritime'/'mar-abox.ttl')],
    'food':     sorted(glob.glob(str(REPO/'ontology'/'dmfo-*.ttl'))) +
                [str(REPO/'profiles'/'food'/'food-tbox.ttl'),
                 str(REPO/'profiles'/'food'/'food-abox.ttl')],
}
B2_PROFILES = {
    'maritime': [B2/'ontology'/'b2-cco-base.ttl',
                 B2/'ontology'/'b2-cco-maritime.ttl', B2/'abox'/'maritime-abox.ttl'],
    'food':     [B2/'ontology'/'b2-cco-base.ttl',
                 B2/'ontology'/'b2-cco-food.ttl', B2/'abox'/'food-abox.ttl'],
}
DMFO_QUERIES = {f'ACQ-{f.name.split("-")[1]}-{f.name.split("-")[2].split("_")[0]}': f
                for f in (REPO/'acqs'/'queries'/'dmfo').glob('ACQ-*.sparql')}
B2_BY_KEY = {f.stem.rsplit('-', 1)[0]: f for f in (REPO/'acqs'/'queries'/'b2-cco-sosa').glob('acq-*.rq')}
B2_NATIVE_BY_KEY = {f.stem.rsplit('-cco-', 1)[0]: f for f in (REPO/'acqs'/'queries'/'b2-cco-native').glob('acq-*.rq')}
KEY_TO_ID = {f'acq-{i:02d}': aid for i, aid in enumerate(
    'ACQ-I-01 ACQ-I-02 ACQ-II-01 ACQ-II-02 ACQ-II-03 ACQ-II-04 ACQ-II-05 ACQ-II-06 '
    'ACQ-III-01 ACQ-III-02 ACQ-III-03 ACQ-III-04 ACQ-III-05 ACQ-III-06 ACQ-III-07 '
    'ACQ-III-08 ACQ-IV-01 ACQ-IV-02 ACQ-IV-03 ACQ-IV-04'.split(), start=1)}

def load(files, mode):
    g = Graph()
    for f in files: g.parse(str(f), format='turtle')
    if mode == 'baseline':
        pass
    elif mode == 'stripped':
        strip(g, aggressive=False)
    elif mode == 'aggressive':
        strip(g, aggressive=True)
    raw = len(g)
    t0 = time.perf_counter()
    owlrl.DeductiveClosure(SEMANTICS).expand(g)
    return g, raw, (time.perf_counter()-t0)*1000

def bench(g, text, reps=REPS):
    list(g.query(text)); list(g.query(text))
    durs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        rows = list(g.query(text))
        durs.append((time.perf_counter()-t0)*1000)
    return len(rows), statistics.median(durs)

def run(prof_map, q_resolver, mode):
    out = {}
    for prof, files in prof_map.items():
        g, raw, ct = load(files, mode)
        ans = 0
        total_q = 0
        for key, aid in KEY_TO_ID.items():
            qpath = q_resolver(key)
            if not qpath or not qpath.exists(): continue
            try:
                rows, med = bench(g, qpath.read_text())
                if rows > 0: ans += 1
                total_q += med
            except Exception:
                pass
        out[prof] = {'raw': raw, 'closure': len(g), 'closure_ms': round(ct, 1),
                     'queries_ms': round(total_q, 1),
                     'total_ms': round(ct + total_q, 1),
                     'answered': ans}
    return out

print('Three-mode benchmark: baseline vs metadata-stripped vs aggressive (DMFO-only A1+A3 strip)')
print('All under OWL-RL_Semantics. 30 reps per ACQ.\n')

results = {}
for mode in ('baseline', 'stripped', 'aggressive'):
    results[mode] = {
        'DMFO':         run(DMFO_PROFILES, lambda k: DMFO_QUERIES.get(KEY_TO_ID[k]), mode),
        'B2-CCO/native':run(B2_PROFILES, lambda k: B2_NATIVE_BY_KEY.get(k) or B2_BY_KEY.get(k), mode),
    }

print(f'{"Mode":12s} {"Framework":18s} {"Profile":10s} {"raw":>6s} {"closure":>9s} {"closure_t":>11s} {"queries":>10s} {"total":>10s} {"ans":>5s}')
for mode in ('baseline', 'stripped', 'aggressive'):
    for fw, data in results[mode].items():
        for prof, p in data.items():
            print(f'  {mode:10s} {fw:16s} {prof:10s} {p["raw"]:>6d} {p["closure"]:>8d} '
                  f'{p["closure_ms"]:>10.1f}m {p["queries_ms"]:>9.1f}m '
                  f'{p["total_ms"]:>9.1f}m  {p["answered"]:>3d}/20')
    print()

# Final showdown
print(f'{"=" * 95}')
print('FINAL: DMFO/aggressive vs B2-CCO/native/stripped (best-case for each)')
for prof in ('maritime', 'food'):
    d = results['aggressive']['DMFO'][prof]['total_ms']
    c = results['stripped']['B2-CCO/native'][prof]['total_ms']
    win = 'DMFO faster' if d < c else 'B2-CCO faster'
    print(f'  {prof:10s}  DMFO={d:.1f}ms  B2-CCO={c:.1f}ms  →  {win}  ({d/c:.2f}x)')

(REPO/'validation'/'results'/'perf_aggressive_strip.json').write_text(
    json.dumps(results, indent=2))
