# Self-contained Jena ARQ benchmark runner.
# Replicates the rdflib scale-benchmark under Apache Jena 5.5 to
# verify that the engine choice does not change the qualitative
# DMFO-vs-B2-CCO performance crossover.
FROM eclipse-temurin:21-jdk

ARG JENA_VERSION=5.5.0
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fsSL "https://archive.apache.org/dist/jena/binaries/apache-jena-${JENA_VERSION}.tar.gz" \
      | tar xz -C /opt && \
    ln -s /opt/apache-jena-${JENA_VERSION} /opt/jena
ENV JENA_HOME=/opt/jena
ENV PATH="${JENA_HOME}/bin:${PATH}"

WORKDIR /work
COPY JenaBenchmark.java /work/
RUN javac -cp "${JENA_HOME}/lib/*" /work/JenaBenchmark.java

ENTRYPOINT ["java", "-cp", "/work:/opt/jena/lib/*", "JenaBenchmark"]
