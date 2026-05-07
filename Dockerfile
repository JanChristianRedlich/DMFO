# =============================================================
# DMFO Reproduction Image
#
# Builds a self-contained image that runs the full DMFO ISWC
# reproduction pipeline (validate_kb, conformance, locality, SHACL,
# 20 ACQs + B1 ablation, HermiT TBox classification).
#
#   docker build -t dmfo:2.0.0 .
#   docker run --rm -v "$PWD/validation/results:/work/validation/results" dmfo:2.0.0
# =============================================================
FROM eclipse-temurin:17-jdk

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY . /work

RUN python3 -m pip install --no-cache-dir --break-system-packages \
        rdflib>=7.0 owlrl>=7.0 owlready2>=0.45 pyshacl>=0.25

# Optional: pre-fetch imported vocabularies into local cache.
RUN bash validation/scripts/fetch_imports.sh || true

ENTRYPOINT ["bash", "validation/scripts/run_queries.sh"]
