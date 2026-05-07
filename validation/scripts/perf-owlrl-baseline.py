#!/usr/bin/env python3
"""Measure current OWL-RL baseline: DMFO vs B2-CCO/sosa vs B2-CCO/native."""
from __future__ import annotations
import json, time, statistics, glob
from pathlib import Path
from rdflib import Graph
import owlrl

REPO = Path(__file__).resolve().parents[2]
B2 = REPO / 'validation' / 'b2-cco'
SEMANTICS = owlrl.OWLRL_Semantics
REPS = 30

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

def load(files):
    g = Graph()
    for f in files: g.parse(str(f), format='turtle')
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

def run(label, prof_map, q_resolver):
    out = {}
    for prof, files in prof_map.items():
        g, raw, ct = load(files)
        out[prof] = {'raw': raw, 'closure': len(g), 'closure_ms': round(ct, 1),
                     'per_acq': {}}
        total_q = 0
        for key, aid in KEY_TO_ID.items():
            qpath = q_resolver(key)
            if not qpath or not qpath.exists(): continue
            try:
                rows, med = bench(g, qpath.read_text())
                out[prof]['per_acq'][aid] = {'rows': rows, 'median_ms': round(med, 3)}
                total_q += med
            except Exception as exc:
                out[prof]['per_acq'][aid] = {'error': str(exc)}
        out[prof]['total_query_ms'] = round(total_q, 1)
        out[prof]['total_pipeline_ms'] = round(ct + total_q, 1)
        print(f'  [{label}/{prof}]  raw={raw}  closure={len(g)}  '
              f'closure_t={ct:.0f}ms  total_q={total_q:.0f}ms  total={ct+total_q:.0f}ms')
    return out

print('Apples-to-apples under OWL-RL_Semantics ...')
results = {
    'DMFO':         run('DMFO', DMFO_PROFILES, lambda k: DMFO_QUERIES.get(KEY_TO_ID[k])),
    'B2-CCO/sosa':  run('sosa', B2_SOSA, lambda k: B2_BY_KEY.get(k)),
    'B2-CCO/native':run('nat',  B2_NATIVE, lambda k: B2_NATIVE_BY_KEY.get(k) or B2_BY_KEY.get(k)),
}

print(f'\n{"=" * 95}')
print(f'{"Framework":18s} {"Profile":10s} {"raw":>6s} {"closure":>9s} {"closure_t":>11s} '
      f'{"queries":>10s} {"total":>10s}')
for fw, data in results.items():
    for prof, p in data.items():
        print(f'  {fw:16s} {prof:10s} {p["raw"]:>6d} {p["closure"]:>8d} '
              f'{p["closure_ms"]:>10.1f}m {p["total_query_ms"]:>9.1f}m '
              f'{p["total_pipeline_ms"]:>9.1f}m')

(REPO/'validation'/'results'/'perf_owlrl_baseline.json').write_text(json.dumps(results, indent=2))
print(f'\nSaved: validation/results/perf_owlrl_baseline.json')
