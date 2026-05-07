#!/usr/bin/env python3
"""
High-rep per-ACQ timing benchmark across DMFO + B2-CCO/sosa + B2-CCO/native.
Reports median, p95, and DMFO/B2-CCO ratio per ACQ + per class.
"""
from __future__ import annotations
import json, time, statistics
from pathlib import Path
from rdflib import Graph
import owlrl

REPO = Path(__file__).resolve().parents[2]
B2 = REPO / 'validation' / 'b2-cco'

DMFO_QUERIES = REPO / 'acqs' / 'queries' / 'dmfo'
B2_QUERIES = REPO / 'acqs' / 'queries' / 'b2-cco-sosa'
B2_NATIVE = REPO / 'acqs' / 'queries' / 'b2-cco-native'

DMFO_PROFILES = {
    'maritime': [
        REPO/'ontology'/'dmfo-base.ttl',
        REPO/'ontology'/'dmfo-identity.ttl',
        REPO/'ontology'/'dmfo-state.ttl',
        REPO/'ontology'/'dmfo-evidence.ttl',
        REPO/'ontology'/'dmfo-context.ttl',
        REPO/'ontology'/'dmfo-activity.ttl',
        REPO/'ontology'/'dmfo-location.ttl',
        REPO/'ontology'/'dmfo-identity-deriv.ttl',
        REPO/'profiles'/'maritime'/'mar-tbox.ttl',
        REPO/'profiles'/'maritime'/'mar-abox.ttl',
    ],
    'food': [
        REPO/'ontology'/'dmfo-base.ttl',
        REPO/'ontology'/'dmfo-identity.ttl',
        REPO/'ontology'/'dmfo-state.ttl',
        REPO/'ontology'/'dmfo-evidence.ttl',
        REPO/'ontology'/'dmfo-context.ttl',
        REPO/'ontology'/'dmfo-activity.ttl',
        REPO/'ontology'/'dmfo-location.ttl',
        REPO/'ontology'/'dmfo-identity-deriv.ttl',
        REPO/'profiles'/'food'/'food-tbox.ttl',
        REPO/'profiles'/'food'/'food-abox.ttl',
    ],
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

# DMFO ACQ filename → ACQ ID
DMFO_QUERY_BY_ID = {}
for f in sorted(DMFO_QUERIES.glob('ACQ-*.sparql')):
    name = f.name
    cls = name.split('-')[1]
    idx = name.split('-')[2].split('_')[0]
    aid = f'ACQ-{cls}-{idx}'
    DMFO_QUERY_BY_ID[aid] = f

# B2-CCO query keys
B2_BY_KEY = {f.stem.rsplit('-', 1)[0]: f for f in B2_QUERIES.glob('acq-*.rq')}
B2_NATIVE_BY_KEY = {f.stem.rsplit('-cco-', 1)[0]: f for f in B2_NATIVE.glob('acq-*.rq')}

# Map B2 keys → ACQ ids (same order as DMFO)
KEY_TO_ID = {
    'acq-01': 'ACQ-I-01',  'acq-02': 'ACQ-I-02',
    'acq-03': 'ACQ-II-01', 'acq-04': 'ACQ-II-02', 'acq-05': 'ACQ-II-03',
    'acq-06': 'ACQ-II-04', 'acq-07': 'ACQ-II-05', 'acq-08': 'ACQ-II-06',
    'acq-09': 'ACQ-III-01', 'acq-10': 'ACQ-III-02', 'acq-11': 'ACQ-III-03',
    'acq-12': 'ACQ-III-04', 'acq-13': 'ACQ-III-05', 'acq-14': 'ACQ-III-06',
    'acq-15': 'ACQ-III-07', 'acq-16': 'ACQ-III-08',
    'acq-17': 'ACQ-IV-01', 'acq-18': 'ACQ-IV-02',
    'acq-19': 'ACQ-IV-03', 'acq-20': 'ACQ-IV-04',
}

def load_kb(files):
    g = Graph()
    for f in files:
        g.parse(str(f), format='turtle')
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return g

def bench_query(g, query_text, reps=20):
    # warm-up (twice)
    list(g.query(query_text))
    list(g.query(query_text))
    durs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        rows = list(g.query(query_text))
        durs.append((time.perf_counter() - t0) * 1000)  # ms
    return {
        'rows': len(rows),
        'median_ms': round(statistics.median(durs), 3),
        'mean_ms': round(statistics.mean(durs), 3),
        'p95_ms': round(sorted(durs)[int(len(durs)*0.95)], 3),
        'min_ms': round(min(durs), 3),
        'max_ms': round(max(durs), 3),
    }

def run_variant(label, profiles_map, query_resolver, profile_filter=None):
    out = {}
    for prof, files in profiles_map.items():
        if profile_filter and prof != profile_filter:
            continue
        print(f'\n  Loading {label} {prof}...', end=' ', flush=True)
        g = load_kb(files)
        print(f'KB: {len(g)} triples (after closure)')
        out[prof] = {}
        for key, aid in KEY_TO_ID.items():
            qpath = query_resolver(key)
            if not qpath or not qpath.exists():
                continue
            text = qpath.read_text()
            try:
                r = bench_query(g, text)
                out[prof][aid] = r
            except Exception as exc:
                out[prof][aid] = {'error': str(exc), 'median_ms': None}
    return out

# DMFO uses ACQ-NN_name.sparql files
def dmfo_resolver(key):
    aid = KEY_TO_ID[key]
    return DMFO_QUERY_BY_ID.get(aid)

def b2_sosa_resolver(key):
    return B2_BY_KEY.get(key)

def b2_native_resolver(key):
    n = B2_NATIVE_BY_KEY.get(key)
    return n if n else B2_BY_KEY.get(key)

print('Benchmarking DMFO + B2-CCO/sosa + B2-CCO/native (20 reps each)...')
results = {
    'DMFO':      run_variant('DMFO', DMFO_PROFILES, dmfo_resolver),
    'B2-sosa':   run_variant('B2/sosa', B2_SOSA_PROFILES, b2_sosa_resolver),
    'B2-native': run_variant('B2/nat', B2_NATIVE_PROFILES, b2_native_resolver),
}

# Report
print('\n' + '='*108)
print(f'{"ACQ":11s}  Cls  | {"DMFO mar":>10s} {"DMFO food":>10s} | {"sosa mar":>10s} {"sosa food":>10s} | {"nat mar":>10s} {"nat food":>10s}')
print('-'*108)
for key, aid in KEY_TO_ID.items():
    cls = aid.split('-')[1]
    row = f'  {aid:11s}  {cls:3s}'
    for variant in ('DMFO', 'B2-sosa', 'B2-native'):
        for prof in ('maritime', 'food'):
            r = results[variant].get(prof, {}).get(aid, {})
            m = r.get('median_ms')
            row += f' | {m:>9.2f}ms' if isinstance(m, (int,float)) else f' | {"--":>11s}'
    print(row)

# Per-class medians
print('\n' + '='*108)
print('PER-CLASS MEDIAN (across both profiles):')
print(f'{"Class":6s}  {"DMFO":>10s}  {"sosa":>10s}  {"native":>10s}  {"ratio sosa/DMFO":>16s}  {"ratio native/DMFO":>18s}')
for cls in 'I II III IV'.split():
    aids = [aid for k,aid in KEY_TO_ID.items() if aid.split('-')[1]==cls]
    def median_for(variant):
        vals = []
        for aid in aids:
            for prof in ('maritime','food'):
                m = results[variant].get(prof, {}).get(aid, {}).get('median_ms')
                if isinstance(m,(int,float)): vals.append(m)
        return statistics.median(vals) if vals else None
    d = median_for('DMFO'); s = median_for('B2-sosa'); n = median_for('B2-native')
    if d:
        print(f'  {cls:4s}  {d:>9.2f}ms  {s:>9.2f}ms  {n:>9.2f}ms  '
              f'{(s/d):>16.2f}x  {(n/d):>18.2f}x')

# Save
out_path = B2 / 'results' / 'b2-cco-perf-detailed.json'
out_path.write_text(json.dumps(results, indent=2))
print(f'\n  Detailed: {out_path.relative_to(REPO)}')

# Per-ACQ ratio table for the multi-bridge queries
print('\n' + '='*108)
print('MULTI-BRIDGE Class III ratios (B2-CCO median / DMFO median, profile-averaged):')
print(f'{"ACQ":11s}  {"DMFO":>9s}  {"sosa ratio":>11s}  {"native ratio":>13s}')
for aid in [a for k,a in KEY_TO_ID.items() if a.startswith('ACQ-III')]:
    def avg(variant):
        vals = []
        for prof in ('maritime','food'):
            m = results[variant].get(prof, {}).get(aid, {}).get('median_ms')
            if isinstance(m,(int,float)): vals.append(m)
        return statistics.mean(vals) if vals else None
    d=avg('DMFO'); s=avg('B2-sosa'); n=avg('B2-native')
    if d and s and n:
        print(f'  {aid:11s}  {d:>8.2f}ms  {(s/d):>10.2f}x  {(n/d):>12.2f}x')
