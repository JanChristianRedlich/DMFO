# Appendix C.2 — ABox Scaling Test (N = 1 … 500)

This is the abridged top-level entry. The full appendix C scaling
report — method, per-size triple counts, pipeline curves, per-ACQ
breakdown at N = 500, Jena cross-engine replication, engine caveats —
lives at:

> [`validation/b2-cco/docs/manuscript-appendix-c-scale-test.md`](../validation/b2-cco/docs/manuscript-appendix-c-scale-test.md)

The detailed appendix is kept inside `validation/b2-cco/docs/` because
it is constructed against the B2-CCO baseline timings; this top-level
file is the navigational anchor and the headline numbers.

---

## Headline result

Pipeline time = closure + 20 ACQs. Both frameworks under symmetric
RDFS metadata-strip. 5 reps median for N ≤ 100; 3 reps for N ∈ {200,
500}.

| N | DMFO RDFS | B2-CCO/native RDFS | Ratio |
|---|---|---|---|
|   1 |   54 ms |   40 ms | 1.35× (DMFO slower) |
|  10 |  128 ms |   93 ms | 1.38× |
|  25 |  279 ms |  203 ms | 1.37× |
|  50 |  522 ms |  419 ms | 1.25× |
| 100 | 1 072 ms | 1 042 ms | 1.03× (parity reached) |
| 200 | 2 325 ms | 2 872 ms | 0.81× (DMFO **faster**) |
| 500 | 8 155 ms | **14 255 ms** | **0.57× (DMFO 1.75× faster)** |

The crossover is at **N ≈ 100** under RDFS. The cause is the four
Class III/IV B2-CCO queries that scale super-linearly because the
CCO baseline routes them through a deep `rdfs:subClassOf*` /
`bfo:has_continuant_part*` property path; DMFO routes them through
typed bridges that the SPARQL engine resolves in O(N).

The same crossover replicates under Apache Jena 5.5.0 (RDFSReasoner
+ ARQ): see the Jena replication section in the linked detailed
appendix.

---

## Reproducibility

```bash
# 1. Generate scaled ABoxes (DMFO + B2-CCO maritime, N = 1, 10, 25,
#    50, 100, 200, 500). Outputs: validation/scale-test/{...}.ttl.
python validation/scripts/generate_scaled_abox.py

# 2. rdflib + owlrl scaling sweep (N = 1, 10, 25, 50, 100). Output:
#    validation/results/scale_benchmark.json.
python validation/scripts/scale-benchmark.py

# 3. Extended sweep N = 200, 500. Output:
#    validation/results/scale_benchmark_large.json (merged into
#    scale_benchmark.json).
python validation/scripts/scale-benchmark-large.py

# 4. Jena cross-engine replication (Docker). Output:
#    validation/results/jena_scale_benchmark.json.
docker build -t dmfo-jena-bench:latest validation/scripts/jena-bench
REPS=3 SIZES="1 10 25 50 100 200 500" \
    bash validation/scripts/jena-bench/run-jena-scale.sh
```

The Jena image (eclipse-temurin:21-jdk + Apache Jena 5.5.0 from the
Apache mirror) is self-contained; no host-side Jena install
required.

---

## Engine caveats

* `OWLMicroReasoner` is the closest Jena reasoner to OWL-RL but is
  not equivalent. Where Jena's row counts differ from rdflib +
  owlrl on a given ACQ, the per-engine difference is documented in
  the detailed appendix's "Engine differences" section.
* The DMFO + Jena combination uses the **typed-bridge** SPARQL
  bodies unchanged. The B2-CCO + Jena combination uses the
  `validation/scripts/jena-bench/queries-native-merged/` overlay so
  that the four strict-CCO-native queries (ACQ-05, 08, 11, 17) are
  exercised in their `(d)`-classified form, not in the SOSA
  co-import form.
