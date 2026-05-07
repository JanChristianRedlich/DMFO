#!/usr/bin/env python3
"""High-rep per-ACQ benchmark: RDFS_Semantics (new default) vs
OWLRL_Semantics (previous default). Reports speedup per class and
per-ACQ where significant."""
from __future__ import annotations
import json, time, statistics, glob
from pathlib import Path
from rdflib import Graph
import owlrl

REPO = Path(__file__).resolve().parents[2]

PROFILES = {
    'maritime': sorted(glob.glob(str(REPO/'ontology'/'dmfo-*.ttl'))) +
                [str(REPO/'profiles'/'maritime'/'mar-tbox.ttl'),
                 str(REPO/'profiles'/'maritime'/'mar-abox.ttl')],
    'food':     sorted(glob.glob(str(REPO/'ontology'/'dmfo-*.ttl'))) +
                [str(REPO/'profiles'/'food'/'food-tbox.ttl'),
                 str(REPO/'profiles'/'food'/'food-abox.ttl')],
}
ACQS = sorted((REPO/'validation'/'sparql').glob('ACQ-*.sparql'))
REPS = 30

def aid_for(p):
    parts = p.name.split('-')
    return f'ACQ-{parts[1]}-{parts[2].split("_")[0]}'

def load(profile, sclass):
    g = Graph()
    for f in PROFILES[profile]:
        g.parse(f, format='turtle')
    t0 = time.perf_counter()
    owlrl.DeductiveClosure(sclass).expand(g)
    return g, len(g), (time.perf_counter()-t0)*1000

def bench(g, text, reps=REPS):
    list(g.query(text)); list(g.query(text))
    durs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        rows = list(g.query(text))
        durs.append((time.perf_counter()-t0)*1000)
    return len(rows), statistics.median(durs)

print(f'{"=" * 95}')
print('Per-ACQ benchmark: RDFS_Semantics (new default) vs OWLRL_Semantics (previous)')
print(f'{"=" * 95}')

results = {}
for profile in ('maritime', 'food'):
    print(f'\n=== Profile: {profile} ===')
    g_rdfs,  size_r, ct_r = load(profile, owlrl.RDFS_Semantics)
    g_owlrl, size_o, ct_o = load(profile, owlrl.OWLRL_Semantics)
    print(f'  closure size:  RDFS={size_r}  OWL-RL={size_o}  '
          f'(saved {(1-size_r/size_o)*100:.0f}%)')
    print(f'  closure time:  RDFS={ct_r:.0f}ms  OWL-RL={ct_o:.0f}ms  '
          f'(speedup {ct_o/ct_r:.1f}x)')
    print()
    print(f'  {"ACQ":11s}  {"RDFS ms":>8s}  {"OWL-RL ms":>10s}  {"speedup":>8s}')
    profile_data = {'closure_rdfs': size_r, 'closure_owlrl': size_o,
                    'closure_time_rdfs': ct_r, 'closure_time_owlrl': ct_o,
                    'per_acq': {}}
    for q in ACQS:
        aid = aid_for(q)
        text = q.read_text()
        try:
            r_rows, r_med = bench(g_rdfs, text)
            o_rows, o_med = bench(g_owlrl, text)
            speedup = o_med / r_med if r_med > 0 else 0
            profile_data['per_acq'][aid] = {
                'rdfs_ms': round(r_med, 3), 'owlrl_ms': round(o_med, 3),
                'speedup': round(speedup, 2),
                'rows_rdfs': r_rows, 'rows_owlrl': o_rows,
            }
            print(f'  {aid:11s}  {r_med:>7.2f}m  {o_med:>9.2f}m  {speedup:>7.2f}x')
        except Exception as exc:
            print(f'  {aid:11s}  ERROR: {exc}')
    results[profile] = profile_data

# Per-class median (across both profiles)
print(f'\n{"=" * 95}')
print('PER-CLASS QUERY MEDIAN — RDFS vs OWL-RL')
print(f'{"Class":7s}  {"RDFS ms":>8s}  {"OWL-RL ms":>10s}  {"speedup":>8s}')
for cls in 'I II III IV'.split():
    rdfs_vals, owlrl_vals = [], []
    for p in ('maritime','food'):
        for aid, r in results[p]['per_acq'].items():
            if aid.split('-')[1] != cls: continue
            rdfs_vals.append(r['rdfs_ms']); owlrl_vals.append(r['owlrl_ms'])
    if rdfs_vals:
        rm = statistics.median(rdfs_vals); om = statistics.median(owlrl_vals)
        print(f'  {cls:5s}    {rm:>7.2f}m  {om:>9.2f}m  {(om/rm):>7.2f}x')

# Total time saved per pipeline run (closure + 20 ACQs)
print(f'\n{"=" * 95}')
print('TOTAL PIPELINE TIME (closure + 20 ACQ queries)')
for p in ('maritime', 'food'):
    pa = results[p]['per_acq']
    rdfs_total = results[p]['closure_time_rdfs'] + sum(r['rdfs_ms'] for r in pa.values())
    owl_total  = results[p]['closure_time_owlrl'] + sum(r['owlrl_ms'] for r in pa.values())
    print(f'  {p:10s}  RDFS={rdfs_total:.0f}ms  OWL-RL={owl_total:.0f}ms  '
          f'(saved {owl_total - rdfs_total:.0f}ms = {(1-rdfs_total/owl_total)*100:.0f}%)')

(REPO/'validation'/'results'/'closure_rdfs_vs_owlrl.json').write_text(
    json.dumps(results, indent=2))
print(f'\nSaved: validation/results/closure_rdfs_vs_owlrl.json')
