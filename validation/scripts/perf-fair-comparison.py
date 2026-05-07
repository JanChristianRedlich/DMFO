#!/usr/bin/env python3
"""Apples-to-apples per-ACQ benchmark: DMFO vs B2-CCO/sosa vs
B2-CCO/native, all running under RDFS_Semantics. 30 reps."""
from __future__ import annotations
import json, time, statistics, glob
from pathlib import Path
from rdflib import Graph
import owlrl

REPO = Path(__file__).resolve().parents[2]
B2 = REPO / 'validation' / 'b2-cco'
SEMANTICS = owlrl.RDFS_Semantics   # parity for both frameworks
REPS = 30

DMFO_PROFILES = {
    'maritime': sorted(glob.glob(str(REPO/'ontology'/'dmfo-*.ttl'))) +
                [str(REPO/'profiles'/'maritime'/'mar-tbox.ttl'),
                 str(REPO/'profiles'/'maritime'/'mar-abox.ttl')],
    'food':     sorted(glob.glob(str(REPO/'ontology'/'dmfo-*.ttl'))) +
                [str(REPO/'profiles'/'food'/'food-tbox.ttl'),
                 str(REPO/'profiles'/'food'/'food-abox.ttl')],
}
B2_SOSA_PROFILES = {
    'maritime': [B2/'ontology'/'b2-cco-base.ttl', B2/'ontology'/'b2-cco-base-sosa.ttl',
                 B2/'ontology'/'b2-cco-maritime.ttl', B2/'abox'/'maritime-abox.ttl'],
    'food':     [B2/'ontology'/'b2-cco-base.ttl', B2/'ontology'/'b2-cco-base-sosa.ttl',
                 B2/'ontology'/'b2-cco-food.ttl', B2/'abox'/'food-abox.ttl'],
}
B2_NATIVE_PROFILES = {
    'maritime': [B2/'ontology'/'b2-cco-base.ttl',
                 B2/'ontology'/'b2-cco-maritime.ttl', B2/'abox'/'maritime-abox.ttl'],
    'food':     [B2/'ontology'/'b2-cco-base.ttl',
                 B2/'ontology'/'b2-cco-food.ttl', B2/'abox'/'food-abox.ttl'],
}

DMFO_QUERY_BY_ID = {}
for f in sorted((REPO/'acqs'/'queries'/'dmfo').glob('ACQ-*.sparql')):
    parts = f.name.split('-')
    DMFO_QUERY_BY_ID[f'ACQ-{parts[1]}-{parts[2].split("_")[0]}'] = f

B2_BY_KEY = {f.stem.rsplit('-', 1)[0]: f for f in (REPO/'acqs'/'queries'/'b2-cco-sosa').glob('acq-*.rq')}
B2_NATIVE_BY_KEY = {f.stem.rsplit('-cco-', 1)[0]: f for f in (REPO/'acqs'/'queries'/'b2-cco-native').glob('acq-*.rq')}
KEY_TO_ID = {f'acq-{i:02d}': aid for i, aid in enumerate(
    'ACQ-I-01 ACQ-I-02 ACQ-II-01 ACQ-II-02 ACQ-II-03 ACQ-II-04 ACQ-II-05 '
    'ACQ-II-06 ACQ-III-01 ACQ-III-02 ACQ-III-03 ACQ-III-04 ACQ-III-05 '
    'ACQ-III-06 ACQ-III-07 ACQ-III-08 ACQ-IV-01 ACQ-IV-02 ACQ-IV-03 ACQ-IV-04'.split(),
    start=1)}

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

def run(label, prof_map, query_resolver):
    out = {}
    for prof, files in prof_map.items():
        g, raw, ct = load(files)
        out[prof] = {'raw': raw, 'closure': len(g), 'closure_ms': round(ct, 2),
                     'per_acq': {}}
        for key, aid in KEY_TO_ID.items():
            qpath = query_resolver(key)
            if not qpath or not qpath.exists(): continue
            try:
                rows, med = bench(g, qpath.read_text())
                out[prof]['per_acq'][aid] = {'rows': rows, 'median_ms': round(med, 3)}
            except Exception as exc:
                out[prof]['per_acq'][aid] = {'error': str(exc)}
        print(f'  [{label}/{prof}] raw={raw} closure={len(g)} '
              f'closure_t={ct:.0f}ms')
    return out

print('Loading + benchmarking under RDFS_Semantics (apples-to-apples)…')
results = {
    'DMFO':         run('DMFO', DMFO_PROFILES, lambda k: DMFO_QUERY_BY_ID.get(KEY_TO_ID[k])),
    'B2-CCO/sosa':  run('sosa', B2_SOSA_PROFILES, lambda k: B2_BY_KEY.get(k)),
    'B2-CCO/native':run('nat',  B2_NATIVE_PROFILES,
                        lambda k: B2_NATIVE_BY_KEY.get(k) or B2_BY_KEY.get(k)),
}

# Closure-size + closure-time table
print(f'\n{"=" * 95}')
print('CLOSURE SIZE + TIME (RDFS_Semantics, apples-to-apples)')
print(f'{"Framework":18s} {"Profile":10s} {"raw":>6s} {"closure":>8s} {"+%":>6s} {"closure ms":>11s}')
for fw, data in results.items():
    for prof, p in data.items():
        delta = (p['closure']-p['raw'])/p['raw']*100
        print(f'  {fw:16s} {prof:10s} {p["raw"]:>6d} {p["closure"]:>8d} {delta:>5.0f}% {p["closure_ms"]:>10.1f}ms')

# Per-class median + ratio (DMFO baseline)
print(f'\n{"=" * 95}')
print('PER-CLASS QUERY MEDIAN (across both profiles), all under RDFS')
print(f'{"Class":7s}  {"DMFO ms":>8s}  {"sosa ms":>8s}  {"nat ms":>8s}  '
      f'{"sosa/DMFO":>10s}  {"nat/DMFO":>10s}')
for cls in 'I II III IV'.split():
    def median_for(fw):
        v = []
        for prof, p in results[fw].items():
            for aid, r in p['per_acq'].items():
                if 'median_ms' in r and aid.split('-')[1] == cls:
                    v.append(r['median_ms'])
        return statistics.median(v) if v else None
    d = median_for('DMFO'); s = median_for('B2-CCO/sosa'); n = median_for('B2-CCO/native')
    print(f'  {cls:5s}    {d:>7.2f}m  {s:>7.2f}m  {n:>7.2f}m  '
          f'{(s/d):>9.2f}x  {(n/d):>9.2f}x')

# Total pipeline (closure + 20 ACQs) for each framework / profile
print(f'\n{"=" * 95}')
print('TOTAL PIPELINE (closure + 20 ACQs), apples-to-apples under RDFS')
print(f'{"Framework":18s} {"Profile":10s} {"closure":>10s} {"queries":>10s} {"total":>10s}')
for fw, data in results.items():
    for prof, p in data.items():
        total_q = sum(r['median_ms'] for r in p['per_acq'].values() if 'median_ms' in r)
        total = p['closure_ms'] + total_q
        print(f'  {fw:16s} {prof:10s} {p["closure_ms"]:>9.0f}ms {total_q:>9.0f}ms {total:>9.0f}ms')

(REPO/'validation'/'results'/'perf_fair_rdfs_comparison.json').write_text(
    json.dumps(results, indent=2))
print(f'\nSaved: validation/results/perf_fair_rdfs_comparison.json')
