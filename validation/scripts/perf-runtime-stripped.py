#!/usr/bin/env python3
"""Apples-to-apples performance benchmark with on-the-fly metadata
stripping applied to BOTH DMFO and B2-CCO. Measures whether the
metadata-strip optimization affects closure time."""
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

def is_doc(p):
    if p in DOC_PREDS: return True
    return any(str(p).startswith(x) for x in DOC_PFX)

def strip(g):
    """Remove owl:Ontology header triples + documentation predicates."""
    onto_iris = set(g.subjects(RDF.type, OWL.Ontology))
    removed = 0
    for s in onto_iris:
        for s2, p, o in list(g.triples((s, None, None))):
            g.remove((s2, p, o)); removed += 1
    for s, p, o in list(g):
        if is_doc(p):
            g.remove((s, p, o)); removed += 1
    return removed

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
                 B2/'ontology'/'b2-cco-maritime.ttl',
                 B2/'abox'/'maritime-abox.ttl'],
    'food':     [B2/'ontology'/'b2-cco-base.ttl',
                 B2/'ontology'/'b2-cco-food.ttl',
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

def load(files, do_strip):
    g = Graph()
    for f in files: g.parse(str(f), format='turtle')
    raw_before = len(g)
    stripped = 0
    if do_strip: stripped = strip(g)
    raw_after = len(g)
    t0 = time.perf_counter()
    owlrl.DeductiveClosure(SEMANTICS).expand(g)
    return g, raw_before, raw_after, stripped, (time.perf_counter()-t0)*1000

def bench(g, text, reps=REPS):
    list(g.query(text)); list(g.query(text))
    durs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        rows = list(g.query(text))
        durs.append((time.perf_counter()-t0)*1000)
    return len(rows), statistics.median(durs)

def run(label, prof_map, q_resolver, do_strip):
    out = {}
    for prof, files in prof_map.items():
        g, rb, ra, stripped, ct = load(files, do_strip)
        per_acq = {}
        total_q = 0
        for key, aid in KEY_TO_ID.items():
            qpath = q_resolver(key)
            if not qpath or not qpath.exists(): continue
            try:
                rows, med = bench(g, qpath.read_text())
                per_acq[aid] = {'rows': rows, 'median_ms': round(med, 3)}
                total_q += med
            except Exception as exc:
                per_acq[aid] = {'error': str(exc)}
        out[prof] = {'raw_before': rb, 'raw_after': ra, 'stripped': stripped,
                     'closure': len(g), 'closure_ms': round(ct, 1),
                     'total_query_ms': round(total_q, 1),
                     'total_pipeline_ms': round(ct + total_q, 1),
                     'per_acq': per_acq}
        print(f'  [{label}/{prof}]  raw={rb}{f"→{ra}" if do_strip else ""}  '
              f'closure={len(g)}  closure_t={ct:.0f}ms  '
              f'queries={total_q:.0f}ms  total={ct+total_q:.0f}ms')
    return out

print(f'\n{"=" * 75}')
print('BASELINE (no strip) — both under OWL-RL_Semantics')
print(f'{"=" * 75}')
baseline = {
    'DMFO':         run('DMFO', DMFO_PROFILES, lambda k: DMFO_QUERIES.get(KEY_TO_ID[k]), False),
    'B2-CCO/native':run('nat',  B2_PROFILES, lambda k: B2_NATIVE_BY_KEY.get(k) or B2_BY_KEY.get(k), False),
}

print(f'\n{"=" * 75}')
print('OPTIMIZED (metadata stripped) — both under OWL-RL_Semantics')
print(f'{"=" * 75}')
optimized = {
    'DMFO':         run('DMFO', DMFO_PROFILES, lambda k: DMFO_QUERIES.get(KEY_TO_ID[k]), True),
    'B2-CCO/native':run('nat',  B2_PROFILES, lambda k: B2_NATIVE_BY_KEY.get(k) or B2_BY_KEY.get(k), True),
}

print(f'\n{"=" * 95}')
print('SUMMARY: total pipeline time (closure + 20 ACQs)')
print(f'{"Framework":18s} {"Profile":10s} {"baseline ms":>12s} {"stripped ms":>12s} {"speedup":>9s}')
for fw in ('DMFO', 'B2-CCO/native'):
    for prof in ('maritime', 'food'):
        b = baseline[fw][prof]['total_pipeline_ms']
        s = optimized[fw][prof]['total_pipeline_ms']
        print(f'  {fw:16s} {prof:10s} {b:>10.1f}m  {s:>10.1f}m  {(b/s):>8.2f}x')

(REPO/'validation'/'results'/'perf_runtime_stripped.json').write_text(
    json.dumps({'baseline': baseline, 'stripped': optimized}, indent=2))
print(f'\nSaved: validation/results/perf_runtime_stripped.json')
