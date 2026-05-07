#!/usr/bin/env python3
"""Final benchmark for Paper Table 2 — measures the production
configuration with the symmetric metadata-strip applied to both
DMFO and B2-CCO. All under OWL-RL_Semantics."""
from __future__ import annotations
import json, time, statistics, glob, os
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, URIRef
import owlrl

REPO = Path(__file__).resolve().parents[2]
B2 = REPO / 'validation' / 'b2-cco'
SEMANTICS = owlrl.OWLRL_Semantics
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
    n = 0
    for s in list(g.subjects(RDF.type, OWL.Ontology)):
        for t in list(g.triples((s, None, None))):
            g.remove(t); n += 1
    tbox = set()
    for t in TBOX_TYPES:
        tbox.update(g.subjects(RDF.type, t))
    for s in tbox:
        for s2, p, o in list(g.triples((s, None, None))):
            if p in DOC or any(str(p).startswith(pfx) for pfx in DOC_PFX):
                g.remove((s2, p, o)); n += 1
    for s, p, o in list(g):
        if any(str(p).startswith(pfx) for pfx in DOC_PFX):
            g.remove((s, p, o)); n += 1
    return n

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
    raw_in = len(g)
    stripped = strip(g)
    raw_out = len(g)
    t0 = time.perf_counter()
    owlrl.DeductiveClosure(SEMANTICS).expand(g)
    return g, raw_in, raw_out, (time.perf_counter()-t0)*1000

def bench(g, text, reps=REPS):
    list(g.query(text)); list(g.query(text))
    durs = []
    for _ in range(reps):
        t0 = time.perf_counter()
        rows = list(g.query(text))
        durs.append((time.perf_counter()-t0)*1000)
    return len(rows), statistics.median(durs)

def run(prof_map, q_resolver):
    out = {}
    for prof, files in prof_map.items():
        g, ri, ro, ct = load(files)
        per_class = {'I':[], 'II':[], 'III':[], 'IV':[]}
        total_q = 0
        ans = 0
        for key, aid in KEY_TO_ID.items():
            qpath = q_resolver(key)
            if not qpath or not qpath.exists(): continue
            try:
                rows, med = bench(g, qpath.read_text())
                per_class[aid.split('-')[1]].append(med)
                total_q += med
                if rows > 0: ans += 1
            except Exception:
                pass
        out[prof] = {
            'raw_loaded': ri, 'raw_stripped': ro, 'closure': len(g),
            'closure_ms': round(ct, 1), 'queries_total_ms': round(total_q, 1),
            'pipeline_ms': round(ct + total_q, 1),
            'class_medians_ms': {c: round(statistics.median(v), 3) for c, v in per_class.items() if v},
            'answered_ge_1_row': ans,
        }
    return out

print('Final Table 2 benchmark — production config (symmetric metadata-strip, OWL-RL).\n')
results = {
    'DMFO':         run(DMFO_PROFILES, lambda k: DMFO_QUERIES.get(KEY_TO_ID[k])),
    'B2-CCO/sosa':  run(B2_SOSA, lambda k: B2_BY_KEY.get(k)),
    'B2-CCO/native':run(B2_NATIVE, lambda k: B2_NATIVE_BY_KEY.get(k) or B2_BY_KEY.get(k)),
}

# Render Table 2
print(f'{"=" * 100}')
print('TABLE 2 — Reasoning-performance metrics (production config; OWL-RL_Semantics; rdflib + owlrl)')
print(f'{"=" * 100}\n')
hdr = f'{"":42s}'
for fw in ('DMFO', 'B2-CCO/sosa', 'B2-CCO/native'):
    hdr += f'{fw:>20s}'
print(hdr)
hdr2 = f'{"Metric":42s}'
for fw in ('DMFO', 'B2-CCO/sosa', 'B2-CCO/native'):
    hdr2 += f'{"Mar.":>10s}{"Food":>10s}'
print(hdr2)
print('-' * 100)

def row(label, key, fmt='%.0f'):
    line = f'  {label:40s}'
    for fw in ('DMFO', 'B2-CCO/sosa', 'B2-CCO/native'):
        for prof in ('maritime', 'food'):
            v = results[fw][prof].get(key, '—')
            if isinstance(v, (int, float)):
                line += f'{(fmt % v):>10s}'
            else:
                line += f'{str(v):>10s}'
    print(line)

def row_class(cls):
    line = f'  Class {cls} median (ms){"":<22s}'
    for fw in ('DMFO', 'B2-CCO/sosa', 'B2-CCO/native'):
        for prof in ('maritime', 'food'):
            v = results[fw][prof]['class_medians_ms'].get(cls, '—')
            line += f'{(("%.2f" % v) if isinstance(v,(int,float)) else str(v)):>10s}'
    print(line)

row('KB raw triples (loaded)', 'raw_loaded')
row('KB raw triples (after strip)', 'raw_stripped')
row('KB closure size (after OWL-RL)', 'closure')
print()
row('Closure expansion time (ms)', 'closure_ms', '%.1f')
print()
for cls in 'I II III IV'.split():
    row_class(cls)
print()
row('Total query time (ms)', 'queries_total_ms', '%.1f')
row('Total pipeline (closure + queries)', 'pipeline_ms', '%.1f')
print()
row('ACQs answered (ge 1 row)', 'answered_ge_1_row')

# Save
out = REPO/'validation'/'results'/'table2_perf.json'
out.write_text(json.dumps(results, indent=2))
print(f'\nSaved: {out.relative_to(REPO)}')
