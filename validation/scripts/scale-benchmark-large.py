#!/usr/bin/env python3
"""Extend scale-benchmark to large N values (200, 500). Reuses the
existing scale_benchmark.json results for N=1..100, appends new
sizes, and reports the extended scaling curve."""
from __future__ import annotations
import json, time, statistics, glob, os, sys
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, URIRef
import owlrl

REPO = Path(__file__).resolve().parents[2]
B2 = REPO / 'validation' / 'b2-cco'
SCALE = REPO / 'validation' / 'scale-test'
RESULTS = REPO / 'validation' / 'results'

REPS = 3  # fewer reps because queries take seconds at scale
NEW_SIZES = [200, 500]
CLOSURES = {'owl-rl': owlrl.OWLRL_Semantics, 'rdfs': owlrl.RDFS_Semantics}

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

DMFO_TBOX = sorted(glob.glob(str(REPO/'ontology'/'dmfo-*.ttl'))) + \
            [str(REPO/'profiles'/'maritime'/'mar-tbox.ttl')]
B2_TBOX_NATIVE = [str(B2/'ontology'/'b2-cco-base.ttl'),
                  str(B2/'ontology'/'b2-cco-maritime.ttl')]
B2_TBOX_SOSA = [str(B2/'ontology'/'b2-cco-base.ttl'),
                str(B2/'ontology'/'b2-cco-base-sosa.ttl'),
                str(B2/'ontology'/'b2-cco-maritime.ttl')]

DMFO_QUERIES = {f'ACQ-{f.name.split("-")[1]}-{f.name.split("-")[2].split("_")[0]}': f
                for f in (REPO/'acqs'/'queries'/'dmfo').glob('ACQ-*.sparql')}
B2_BY_KEY = {f.stem.rsplit('-', 1)[0]: f for f in (REPO/'acqs'/'queries'/'b2-cco-sosa').glob('acq-*.rq')}
B2_NATIVE_BY_KEY = {f.stem.rsplit('-cco-', 1)[0]: f for f in (REPO/'acqs'/'queries'/'b2-cco-native').glob('acq-*.rq')}
KEY_TO_ID = {f'acq-{i:02d}': aid for i, aid in enumerate(
    'ACQ-I-01 ACQ-I-02 ACQ-II-01 ACQ-II-02 ACQ-II-03 ACQ-II-04 ACQ-II-05 ACQ-II-06 '
    'ACQ-III-01 ACQ-III-02 ACQ-III-03 ACQ-III-04 ACQ-III-05 ACQ-III-06 ACQ-III-07 '
    'ACQ-III-08 ACQ-IV-01 ACQ-IV-02 ACQ-IV-03 ACQ-IV-04'.split(), start=1)}

def load(tbox_files, abox_path, semantics):
    g = Graph()
    for f in tbox_files:
        g.parse(f, format='turtle')
    g.parse(str(abox_path), format='turtle')
    strip(g)
    raw = len(g)
    t0 = time.perf_counter()
    owlrl.DeductiveClosure(semantics).expand(g)
    return g, raw, (time.perf_counter()-t0)*1000

def bench(g, text, reps=REPS):
    list(g.query(text))
    durs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        rows = list(g.query(text))
        durs.append((time.perf_counter()-t0)*1000)
    return len(rows), statistics.median(durs)

def run_one(tbox_files, abox_path, q_resolver, semantics):
    g, raw, ct = load(tbox_files, abox_path, semantics)
    per_class = {'I':[], 'II':[], 'III':[], 'IV':[]}
    per_acq = {}
    total_q = 0.0
    for key, aid in KEY_TO_ID.items():
        qpath = q_resolver(key)
        if not qpath or not qpath.exists(): continue
        try:
            rows, med = bench(g, qpath.read_text())
            per_class[aid.split('-')[1]].append(med)
            per_acq[aid] = {'rows': rows, 'median_ms': round(med, 3)}
            total_q += med
        except Exception as exc:
            per_acq[aid] = {'error': str(exc)}
    return {
        'raw': raw, 'closure': len(g), 'closure_ms': round(ct, 1),
        'queries_total_ms': round(total_q, 1),
        'pipeline_ms': round(ct + total_q, 1),
        'class_medians_ms': {c: round(statistics.median(v), 3) for c, v in per_class.items() if v},
        'per_acq': per_acq,
    }

# Load existing results
existing_path = RESULTS / 'scale_benchmark.json'
if existing_path.exists():
    results = json.load(open(existing_path))
else:
    results = {}

for N in NEW_SIZES:
    print(f'\n=== N = {N} containers ===')
    dmfo_abox = SCALE / f'dmfo-maritime-N{N:03d}.ttl'
    b2_abox = SCALE / f'b2cco-maritime-N{N:03d}.ttl'
    if not dmfo_abox.exists() or not b2_abox.exists():
        print(f'  ABox missing — run generate_scaled_abox.py first')
        continue
    results[str(N)] = {}
    for cname, sem in CLOSURES.items():
        results[str(N)][cname] = {}
        # DMFO
        t0 = time.perf_counter()
        r = run_one(DMFO_TBOX, dmfo_abox,
                    lambda k: DMFO_QUERIES.get(KEY_TO_ID[k]), sem)
        wall = time.perf_counter() - t0
        results[str(N)][cname]['DMFO'] = r
        print(f'  DMFO     [{cname:6s}] raw={r["raw"]:>5d} closure={r["closure"]:>6d} '
              f'closure_t={r["closure_ms"]:>7.0f}ms queries={r["queries_total_ms"]:>7.0f}ms '
              f'total={r["pipeline_ms"]:>8.0f}ms  (wall {wall:.1f}s)')
        # B2-sosa
        t0 = time.perf_counter()
        r = run_one(B2_TBOX_SOSA, b2_abox,
                    lambda k: B2_BY_KEY.get(k), sem)
        wall = time.perf_counter() - t0
        results[str(N)][cname]['B2-sosa'] = r
        print(f'  B2-sosa  [{cname:6s}] raw={r["raw"]:>5d} closure={r["closure"]:>6d} '
              f'closure_t={r["closure_ms"]:>7.0f}ms queries={r["queries_total_ms"]:>7.0f}ms '
              f'total={r["pipeline_ms"]:>8.0f}ms  (wall {wall:.1f}s)')
        # B2-native
        t0 = time.perf_counter()
        r = run_one(B2_TBOX_NATIVE, b2_abox,
                    lambda k: B2_NATIVE_BY_KEY.get(k) or B2_BY_KEY.get(k), sem)
        wall = time.perf_counter() - t0
        results[str(N)][cname]['B2-native'] = r
        print(f'  B2-native[{cname:6s}] raw={r["raw"]:>5d} closure={r["closure"]:>6d} '
              f'closure_t={r["closure_ms"]:>7.0f}ms queries={r["queries_total_ms"]:>7.0f}ms '
              f'total={r["pipeline_ms"]:>8.0f}ms  (wall {wall:.1f}s)')

(RESULTS / 'scale_benchmark.json').write_text(json.dumps(results, indent=2, default=str))

# Final scaling curve over all N
print(f'\n{"=" * 100}')
print('EXTENDED SCALING CURVE: total pipeline time (ms) vs N (containers)')
print(f'{"=" * 100}')
print(f'{"N":>5s} | {"DMFO/owl-rl":>12s} {"B2-nat/owl-rl":>14s} {"ratio":>7s} | '
      f'{"DMFO/rdfs":>11s} {"B2-nat/rdfs":>12s} {"ratio":>7s}')
print('-' * 100)
all_sizes = sorted([int(k) for k in results.keys()])
for N in all_sizes:
    r = results[str(N)]
    if 'owl-rl' not in r or 'DMFO' not in r['owl-rl']: continue
    d_owl = r['owl-rl']['DMFO']['pipeline_ms']
    n_owl = r['owl-rl']['B2-native']['pipeline_ms']
    d_rdf = r['rdfs']['DMFO']['pipeline_ms']
    n_rdf = r['rdfs']['B2-native']['pipeline_ms']
    print(f'{N:>5d} | {d_owl:>10.0f}ms {n_owl:>12.0f}ms {(d_owl/n_owl):>6.2f}x | '
          f'{d_rdf:>9.0f}ms {n_rdf:>10.0f}ms {(d_rdf/n_rdf):>6.2f}x')

# Per-class at largest N
N_max = max(all_sizes)
print(f'\nPer-class median at N={N_max} (OWL-RL):')
print(f'{"Class":7s} {"DMFO ms":>9s} {"B2-nat ms":>10s} {"Ratio":>7s}')
for c in 'I II III IV'.split():
    d = results[str(N_max)]['owl-rl']['DMFO']['class_medians_ms'].get(c, 0)
    n = results[str(N_max)]['owl-rl']['B2-native']['class_medians_ms'].get(c, 0)
    print(f'  {c:5s}  {d:>8.2f}m  {n:>9.2f}m  {(d/n if n else 0):>6.2f}x')

print(f'\nPer-class median at N={N_max} (RDFS):')
print(f'{"Class":7s} {"DMFO ms":>9s} {"B2-nat ms":>10s} {"Ratio":>7s}')
for c in 'I II III IV'.split():
    d = results[str(N_max)]['rdfs']['DMFO']['class_medians_ms'].get(c, 0)
    n = results[str(N_max)]['rdfs']['B2-native']['class_medians_ms'].get(c, 0)
    print(f'  {c:5s}  {d:>8.2f}m  {n:>9.2f}m  {(d/n if n else 0):>6.2f}x')
