#!/usr/bin/env bash
# Driver for the Jena scale-replication. Iterates N ∈ {1,10,25,50,100,200,500}
# × {DMFO, B2-CCO/native} × {rdfs, owl-micro}, dispatches each config
# into the dmfo-jena-bench Docker container, collects per-config JSON
# into a single results file.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
mkdir -p validation/results

OUT="validation/results/jena_scale_benchmark.json"
SIZES=(${SIZES:-1 10 25 50 100 200 500})
REPS="${REPS:-3}"
REASONERS=(${REASONERS:-rdfs owl-micro})
IMAGE="${IMAGE:-dmfo-jena-bench:latest}"

# Pre-compute DMFO TBox file list (8 modules + maritime profile-tbox)
DMFO_TBOX_FILES=()
for f in ontology/dmfo-base.ttl ontology/dmfo-identity.ttl ontology/dmfo-state.ttl \
         ontology/dmfo-evidence.ttl ontology/dmfo-context.ttl ontology/dmfo-activity.ttl \
         ontology/dmfo-location.ttl ontology/dmfo-identity-deriv.ttl \
         profiles/maritime/mar-tbox.ttl; do
    DMFO_TBOX_FILES+=("/work/data/$f")
done
DMFO_TBOX=$(IFS=, ; echo "${DMFO_TBOX_FILES[*]}")

# B2-CCO/native TBox: base + maritime
B2_TBOX_FILES=(
    "/work/data/validation/b2-cco/ontology/b2-cco-base.ttl"
    "/work/data/validation/b2-cco/ontology/b2-cco-maritime.ttl"
)
B2_TBOX=$(IFS=, ; echo "${B2_TBOX_FILES[*]}")

results="["
first=1

for N in "${SIZES[@]}"; do
    Npad=$(printf "%03d" "$N")
    for reasoner in "${REASONERS[@]}"; do
        for fw in DMFO B2-CCO-native; do
            if [ "$fw" = "DMFO" ]; then
                tbox="$DMFO_TBOX"
                abox="/work/data/validation/scale-test/dmfo-maritime-N${Npad}.ttl"
                queries="/work/data/acqs/queries/dmfo"
            else
                tbox="$B2_TBOX"
                abox="/work/data/validation/scale-test/b2cco-maritime-N${Npad}.ttl"
                # Use the native-variant overlay dir so the 4 strict-native
                # ACQs (05/08/11/17) are exercised (the SOSA versions are
                # the ones in b2-cco/queries/ — overlay here replaces them)
                queries="/work/data/validation/scripts/jena-bench/queries-native-merged"
            fi
            label="${fw}/N${N}/${reasoner}"
            echo ">>> $label"
            json=$(docker run --rm -v "$ROOT:/work/data:ro" "$IMAGE" \
                "$tbox" "$abox" "$queries" "$reasoner" "$REPS" "$label" 2>&1 | tail -1)
            if [ "$first" -eq 0 ]; then
                results+=","
            fi
            results+=$'\n  '"$json"
            first=0
            # quick echo of result summary
            python3 -c "
import json,sys
try:
    d = json.loads('''$json''')
    print(f'    raw={d.get(\"raw_triples\",\"?\")}  closure={d.get(\"closure_triples\",\"?\")}'
          f'  closure_t={d.get(\"closure_ms\",0):.0f}ms'
          f'  queries={d.get(\"queries_total_ms\",0):.0f}ms'
          f'  total={d.get(\"pipeline_ms\",0):.0f}ms')
except Exception as e:
    print(f'    parse-error: {e}')
    print(f'    raw output: $json'[:200])
"
        done
    done
done

results+="
]"
printf '%s\n' "$results" > "$OUT"
echo
echo "Saved: $OUT"
