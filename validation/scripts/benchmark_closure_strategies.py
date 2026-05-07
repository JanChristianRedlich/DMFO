#!/usr/bin/env python3
"""
Benchmark DMFO closure strategies. Compares:
  (1) no closure
  (2) RDFS_Semantics  (sub-class + sub-property only)
  (3) RDFS_OWLRL_Semantics  (current default — full OWL 2 RL)

For each strategy: closure size + closure time + per-ACQ median.
Reports which ACQs lose answerability under reduced closures so we
know which entailments are actually load-bearing.
"""
from __future__ import annotations
import json, time, statistics, sys, glob
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

STRATEGIES = {
    'none':     None,
    'rdfs':     owlrl.RDFS_Semantics,
    'rdfs+rl':  owlrl.RDFS_OWLRL_Semantics,
    'owl-rl':   owlrl.OWLRL_Semantics,
}

REPS = 20

def load_kb(profile, strategy):
    g = Graph()
    for f in PROFILES[profile]:
        g.parse(f, format='turtle')
    raw = len(g)
    t0 = time.perf_counter()
    if strategy:
        owlrl.DeductiveClosure(strategy).expand(g)
    closure_t = time.perf_counter() - t0
    return g, raw, closure_t

def bench(g, text, reps=REPS):
    list(g.query(text)); list(g.query(text))   # warm-up
    durs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        rows = list(g.query(text))
        durs.append((time.perf_counter() - t0) * 1000)
    return len(rows), statistics.median(durs)

def aid_for(p):
    parts = p.name.split('-')
    return f'ACQ-{parts[1]}-{parts[2].split("_")[0]}'

def status(rows, classification='?'):
    return ('✓' if rows > 0 else '◑')

results = {}
for profile in ('maritime', 'food'):
    print(f'\n=== Profile: {profile} ===')
    print(f'{"strategy":12s} {"raw":>6s} {"closure":>7s} {"closure_ms":>11s} {"median":>10s} {"answered":>10s}')

    profile_results = {}
    for sname, sclass in STRATEGIES.items():
        g, raw, closure_t = load_kb(profile, sclass)
        per_acq = {}
        ans_count = 0
        medians = []
        for q in ACQS:
            aid = aid_for(q)
            text = q.read_text()
            try:
                rows, med = bench(g, text)
                per_acq[aid] = {'rows': rows, 'median_ms': round(med, 3)}
                if rows > 0: ans_count += 1
                medians.append(med)
            except Exception as exc:
                per_acq[aid] = {'error': str(exc)}
        overall_med = statistics.median(medians) if medians else None
        print(f'  {sname:10s} {raw:>6d} {len(g):>7d} {closure_t*1000:>10.1f}ms '
              f'{overall_med:>9.2f}ms  {ans_count:>2d}/{len(ACQS)}')
        profile_results[sname] = {'raw': raw, 'closure': len(g),
                                   'closure_ms': round(closure_t*1000, 1),
                                   'overall_median_ms': round(overall_med, 3),
                                   'answered': ans_count, 'per_acq': per_acq}
    results[profile] = profile_results

# Coverage diff: which ACQs each strategy LOSES vs OWL-RL
print(f'\n{"="*70}')
print('COVERAGE DIFF (ACQs lost vs full OWL-RL):')
for profile in ('maritime', 'food'):
    base = results[profile]['owl-rl']['per_acq']
    base_answered = {a for a, r in base.items() if r.get('rows', 0) > 0}
    print(f'\n  {profile}:')
    for sname in ('none', 'rdfs', 'rdfs+rl'):
        new = results[profile][sname]['per_acq']
        new_answered = {a for a, r in new.items() if r.get('rows', 0) > 0}
        lost = sorted(base_answered - new_answered)
        gained = sorted(new_answered - base_answered)
        print(f'    {sname:10s}: lost={lost or "—"}  gained={gained or "—"}')

# Per-class median per strategy
print(f'\n{"="*70}')
print('PER-CLASS MEDIAN MS (across both profiles):')
print(f'{"strategy":12s} {"I":>8s} {"II":>8s} {"III":>8s} {"IV":>8s} {"all":>8s}')
for sname in STRATEGIES:
    cls_meds = {c: [] for c in 'I II III IV'.split()}
    all_meds = []
    for profile in ('maritime', 'food'):
        for aid, r in results[profile][sname]['per_acq'].items():
            if 'median_ms' in r:
                cls = aid.split('-')[1]
                cls_meds[cls].append(r['median_ms'])
                all_meds.append(r['median_ms'])
    out = f'  {sname:10s}'
    for cls in 'I II III IV'.split():
        m = statistics.median(cls_meds[cls]) if cls_meds[cls] else 0
        out += f' {m:>7.2f}m'
    om = statistics.median(all_meds) if all_meds else 0
    out += f' {om:>7.2f}m'
    print(out)

(REPO / 'validation' / 'results' / 'closure_strategy_benchmark.json').write_text(
    json.dumps(results, indent=2))
print(f'\nSaved: validation/results/closure_strategy_benchmark.json')
