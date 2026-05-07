#!/usr/bin/env python3
"""Symmetric RDFS_Semantics test: do B2-CCO variants lose ACQs that
they answered under OWL-RL? If so, the asymmetry is itself a finding
(B2-CCO depends on OWL-RL features that DMFO doesn't need)."""
from __future__ import annotations
import json, time, statistics, glob
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, URIRef
import owlrl

REPO = Path(__file__).resolve().parents[2]
B2 = REPO / 'validation' / 'b2-cco'
REPS = 30

DOC = {RDFS.label, RDFS.comment, RDFS.isDefinedBy, RDFS.seeAlso,
       URIRef('http://www.w3.org/2004/02/skos/core#scopeNote'),
       URIRef('http://www.w3.org/2004/02/skos/core#closeMatch'),
       URIRef('http://www.w3.org/2004/02/skos/core#exactMatch')}
DOC_PFX = ('http://purl.org/dc/terms/', 'http://purl.org/vocab/vann/')
TBOX_TYPES = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty,
              OWL.AnnotationProperty, OWL.FunctionalProperty,
              OWL.InverseFunctionalProperty, OWL.SymmetricProperty,
              OWL.TransitiveProperty, OWL.IrreflexiveProperty, RDFS.Class}

def strip(g):
    for s in list(g.subjects(RDF.type, OWL.Ontology)):
        for t in list(g.triples((s, None, None))):
            g.remove(t)
    tbox = set()
    for t in TBOX_TYPES:
        tbox.update(g.subjects(RDF.type, t))
    for s in tbox:
        for s2, p, o in list(g.triples((s, None, None))):
            if p in DOC or any(str(p).startswith(pfx) for pfx in DOC_PFX):
                g.remove((s2, p, o))
    for s, p, o in list(g):
        if any(str(p).startswith(pfx) for pfx in DOC_PFX):
            g.remove((s, p, o))

DMFO_PROFILES = {
    'maritime': sorted(glob.glob(str(REPO/'ontology'/'dmfo-*.ttl'))) +
                [str(REPO/'profiles'/'maritime'/'mar-tbox.ttl'),
                 str(REPO/'profiles'/'maritime'/'mar-abox.ttl')],
    'food':     sorted(glob.glob(str(REPO/'ontology'/'dmfo-*.ttl'))) +
                [str(REPO/'profiles'/'food'/'food-tbox.ttl'),
                 str(REPO/'profiles'/'food'/'food-abox.ttl')],
}
B2_SOSA = {
    'maritime': [B2/'ontology'/'b2-cco-base.ttl', B2/'ontology'/'b2-cco-base-sosa.ttl',
                 B2/'ontology'/'b2-cco-maritime.ttl', B2/'abox'/'maritime-abox.ttl'],
    'food':     [B2/'ontology'/'b2-cco-base.ttl', B2/'ontology'/'b2-cco-base-sosa.ttl',
                 B2/'ontology'/'b2-cco-food.ttl', B2/'abox'/'food-abox.ttl'],
}
B2_NATIVE = {
    'maritime': [B2/'ontology'/'b2-cco-base.ttl', B2/'ontology'/'b2-cco-maritime.ttl',
                 B2/'abox'/'maritime-abox.ttl'],
    'food':     [B2/'ontology'/'b2-cco-base.ttl', B2/'ontology'/'b2-cco-food.ttl',
                 B2/'abox'/'food-abox.ttl'],
}
DMFO_QUERIES = {f'ACQ-{f.name.split("-")[1]}-{f.name.split("-")[2].split("_")[0]}': f
                for f in (REPO/'acqs'/'queries'/'dmfo').glob('ACQ-*.sparql')}
B2_BY_KEY = {f.stem.rsplit('-', 1)[0]: f for f in (REPO/'acqs'/'queries'/'b2-cco-sosa').glob('acq-*.rq')}
B2_NATIVE_BY_KEY = {f.stem.rsplit('-cco-', 1)[0]: f for f in (REPO/'acqs'/'queries'/'b2-cco-native').glob('acq-*.rq')}
KEY_TO_ID = {f'acq-{i:02d}': aid for i, aid in enumerate(
    'ACQ-I-01 ACQ-I-02 ACQ-II-01 ACQ-II-02 ACQ-II-03 ACQ-II-04 ACQ-II-05 ACQ-II-06 '
    'ACQ-III-01 ACQ-III-02 ACQ-III-03 ACQ-III-04 ACQ-III-05 ACQ-III-06 ACQ-III-07 '
    'ACQ-III-08 ACQ-IV-01 ACQ-IV-02 ACQ-IV-03 ACQ-IV-04'.split(), start=1)}

def load(files, semantics):
    g = Graph()
    for f in files: g.parse(str(f), format='turtle')
    strip(g)
    t0 = time.perf_counter()
    owlrl.DeductiveClosure(semantics).expand(g)
    return g, len(g), (time.perf_counter()-t0)*1000

def bench(g, text, reps=REPS):
    list(g.query(text)); list(g.query(text))
    durs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        rows = list(g.query(text))
        durs.append((time.perf_counter()-t0)*1000)
    return len(rows), statistics.median(durs)

def run(prof_map, q_resolver, semantics):
    out = {}
    for prof, files in prof_map.items():
        g, closure, ct = load(files, semantics)
        per_acq = {}
        total_q = 0
        ans = 0
        for key, aid in KEY_TO_ID.items():
            qpath = q_resolver(key)
            if not qpath or not qpath.exists(): continue
            try:
                rows, med = bench(g, qpath.read_text())
                per_acq[aid] = {'rows': rows, 'median_ms': round(med, 3)}
                total_q += med
                if rows > 0: ans += 1
            except Exception as exc:
                per_acq[aid] = {'error': str(exc)}
        out[prof] = {'closure': closure, 'closure_ms': round(ct, 1),
                     'queries_ms': round(total_q, 1),
                     'pipeline_ms': round(ct + total_q, 1),
                     'rows_ge_1': ans, 'per_acq': per_acq}
    return out

results = {}
for sname, sem in [('OWL-RL', owlrl.OWLRL_Semantics),
                    ('RDFS',   owlrl.RDFS_Semantics)]:
    print(f'\n=== Closure: {sname} ===')
    results[sname] = {
        'DMFO':         run(DMFO_PROFILES, lambda k: DMFO_QUERIES.get(KEY_TO_ID[k]), sem),
        'B2-CCO/sosa':  run(B2_SOSA, lambda k: B2_BY_KEY.get(k), sem),
        'B2-CCO/native':run(B2_NATIVE, lambda k: B2_NATIVE_BY_KEY.get(k) or B2_BY_KEY.get(k), sem),
    }
    for fw, data in results[sname].items():
        for prof, p in data.items():
            print(f'  [{fw:14s}/{prof:8s}] closure={p["closure"]:>4d} '
                  f'closure_t={p["closure_ms"]:>5.1f}ms  queries={p["queries_ms"]:>5.1f}ms '
                  f'total={p["pipeline_ms"]:>6.1f}ms  rows≥1: {p["rows_ge_1"]:>2d}/20')

# Coverage diff per ACQ between OWL-RL and RDFS
print(f'\n{"=" * 95}')
print('COVERAGE DIFF: which ACQs lose row-bindings under RDFS_Semantics vs OWL-RL?')
for fw in ('DMFO', 'B2-CCO/sosa', 'B2-CCO/native'):
    print(f'\n  {fw}:')
    for prof in ('maritime', 'food'):
        owlrl_acqs = {a for a, r in results['OWL-RL'][fw][prof]['per_acq'].items()
                      if r.get('rows', 0) > 0}
        rdfs_acqs  = {a for a, r in results['RDFS'][fw][prof]['per_acq'].items()
                      if r.get('rows', 0) > 0}
        lost = sorted(owlrl_acqs - rdfs_acqs)
        gained = sorted(rdfs_acqs - owlrl_acqs)
        if lost or gained:
            print(f'    {prof:9s}: lost-under-RDFS={lost or "—"}  gained-under-RDFS={gained or "—"}')
        else:
            print(f'    {prof:9s}: identical answer set under both closures')

# Pipeline-time comparison
print(f'\n{"=" * 95}')
print('PIPELINE-TIME COMPARISON (closure + 20 ACQs, ms, both under symmetric strip)')
print(f'{"":18s} {"OWL-RL mar.":>12s} {"OWL-RL food":>12s} {"RDFS mar.":>11s} {"RDFS food":>11s}'
      f' {"Mar. ratio":>11s} {"Food ratio":>11s}')
for fw in ('DMFO', 'B2-CCO/sosa', 'B2-CCO/native'):
    o_m = results['OWL-RL'][fw]['maritime']['pipeline_ms']
    o_f = results['OWL-RL'][fw]['food']['pipeline_ms']
    r_m = results['RDFS'][fw]['maritime']['pipeline_ms']
    r_f = results['RDFS'][fw]['food']['pipeline_ms']
    print(f'  {fw:16s} {o_m:>10.1f}ms {o_f:>10.1f}ms {r_m:>9.1f}ms {r_f:>9.1f}ms '
          f'{(o_m/r_m):>10.2f}x {(o_f/r_f):>10.2f}x')

(REPO/'validation'/'results'/'perf_rdfs_symmetric.json').write_text(
    json.dumps(results, indent=2))
print(f'\nSaved: validation/results/perf_rdfs_symmetric.json')
