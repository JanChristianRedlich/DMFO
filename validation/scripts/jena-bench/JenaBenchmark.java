/*
 * Jena ARQ scale-benchmark for DMFO vs B2-CCO replication.
 *
 * Mirrors the rdflib + owlrl benchmark in
 * `validation/scripts/scale-benchmark{,-large}.py`. Loads a TBox + ABox
 * pair, applies an inference model (RDFSReasoner or OWL Micro) to
 * materialise the closure, then executes the 20 ACQ queries
 * sequentially with timed medians.
 *
 * Args (positional):
 *   1. comma-separated TBox files (relative to /work/data)
 *   2. ABox file (relative to /work/data)
 *   3. queries directory (relative to /work/data)
 *   4. reasoner: "rdfs" | "owl-micro" | "owl-mini" | "none"
 *   5. reps (int)
 *   6. label (printed in JSON)
 *
 * Output: single-line JSON to stdout.
 */

import org.apache.jena.rdf.model.*;
import org.apache.jena.reasoner.Reasoner;
import org.apache.jena.reasoner.ReasonerRegistry;
import org.apache.jena.query.*;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.Lang;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;

public class JenaBenchmark {

    public static void main(String[] args) throws Exception {
        String tboxArg     = args[0];
        String aboxArg     = args[1];
        String queriesDir  = args[2];
        String reasonerArg = args[3];
        int reps           = Integer.parseInt(args[4]);
        String label       = args[5];

        // 1. Load TBox + ABox into a single Model
        Model base = ModelFactory.createDefaultModel();
        for (String tbox : tboxArg.split(",")) {
            try (InputStream in = Files.newInputStream(Paths.get(tbox.trim()))) {
                RDFDataMgr.read(base, in, Lang.TURTLE);
            }
        }
        try (InputStream in = Files.newInputStream(Paths.get(aboxArg))) {
            RDFDataMgr.read(base, in, Lang.TURTLE);
        }
        long rawTriples = base.size();

        // 2. Wrap with reasoner + force materialisation by counting triples
        long t0 = System.nanoTime();
        Model effective;
        switch (reasonerArg) {
            case "rdfs":
                Reasoner rdfs = ReasonerRegistry.getRDFSReasoner();
                effective = ModelFactory.createInfModel(rdfs, base);
                break;
            case "owl-micro":
                Reasoner micro = ReasonerRegistry.getOWLMicroReasoner();
                effective = ModelFactory.createInfModel(micro, base);
                break;
            case "owl-mini":
                Reasoner mini = ReasonerRegistry.getOWLMiniReasoner();
                effective = ModelFactory.createInfModel(mini, base);
                break;
            default:
                effective = base;
                break;
        }
        long closureTriples = effective.size();   // forces inference
        long closureNs = System.nanoTime() - t0;

        // 3. Run all ACQ queries, time medians over `reps` iterations
        List<Path> queryPaths;
        try (var stream = Files.list(Paths.get(queriesDir))) {
            queryPaths = stream
                .filter(p -> p.toString().endsWith(".sparql") || p.toString().endsWith(".rq"))
                .sorted()
                .collect(Collectors.toList());
        }

        StringBuilder json = new StringBuilder();
        json.append("{\"label\":\"").append(label).append("\",");
        json.append("\"reasoner\":\"").append(reasonerArg).append("\",");
        json.append("\"raw_triples\":").append(rawTriples).append(",");
        json.append("\"closure_triples\":").append(closureTriples).append(",");
        json.append("\"closure_ms\":").append(closureNs / 1_000_000.0).append(",");
        json.append("\"per_acq\":{");

        long totalQueryNs = 0;
        boolean firstAcq = true;
        for (Path qPath : queryPaths) {
            String aid = aidFor(qPath.getFileName().toString());
            String qText = Files.readString(qPath);

            // Warm-up: parse + execute once
            int warmRows = 0;
            try {
                Query q = QueryFactory.create(qText);
                try (QueryExecution qe = QueryExecutionFactory.create(q, effective)) {
                    ResultSet rs = qe.execSelect();
                    while (rs.hasNext()) { rs.next(); warmRows++; }
                }
            } catch (Exception e) {
                appendAcqError(json, firstAcq, aid, e);
                firstAcq = false;
                continue;
            }

            long[] durs = new long[reps];
            int rows = warmRows;
            for (int i = 0; i < reps; i++) {
                long s = System.nanoTime();
                Query q = QueryFactory.create(qText);
                int r = 0;
                try (QueryExecution qe = QueryExecutionFactory.create(q, effective)) {
                    ResultSet rs = qe.execSelect();
                    while (rs.hasNext()) { rs.next(); r++; }
                }
                durs[i] = System.nanoTime() - s;
                rows = r;
            }
            Arrays.sort(durs);
            long medianNs = durs[durs.length / 2];
            totalQueryNs += medianNs;

            if (!firstAcq) json.append(",");
            firstAcq = false;
            json.append("\"").append(aid).append("\":{")
                .append("\"rows\":").append(rows).append(",")
                .append("\"median_ms\":").append(medianNs / 1_000_000.0)
                .append("}");
        }
        json.append("},");
        json.append("\"queries_total_ms\":").append(totalQueryNs / 1_000_000.0).append(",");
        json.append("\"pipeline_ms\":")
            .append((closureNs + totalQueryNs) / 1_000_000.0);
        json.append("}");
        System.out.println(json.toString());
    }

    /** Map filename like "ACQ-III-04_causal_antecedent.sparql" or
     *  "acq-12-cco.rq" to a canonical "ACQ-III-04" identifier. */
    private static String aidFor(String filename) {
        // DMFO-side: ACQ-III-04_causal.sparql
        if (filename.startsWith("ACQ-")) {
            String[] parts = filename.split("-", 3);
            String idx = parts[2].split("_")[0];
            return "ACQ-" + parts[1] + "-" + idx;
        }
        // B2-CCO-side: acq-12-cco.rq → mapping table
        if (filename.startsWith("acq-")) {
            String num = filename.substring(4, 6);
            int n = Integer.parseInt(num);
            String[] cls = {"I","I","II","II","II","II","II","II",
                            "III","III","III","III","III","III","III","III",
                            "IV","IV","IV","IV"};
            String[] idx = {"01","02","01","02","03","04","05","06",
                            "01","02","03","04","05","06","07","08",
                            "01","02","03","04"};
            int i = n - 1;
            return "ACQ-" + cls[i] + "-" + idx[i];
        }
        return filename;
    }

    private static void appendAcqError(StringBuilder json, boolean first, String aid, Exception e) {
        if (!first) json.append(",");
        String msg = e.getMessage() == null ? e.getClass().getSimpleName()
                   : e.getMessage().replace("\"", "\\\"").replace("\n", " ");
        json.append("\"").append(aid).append("\":{\"error\":\"")
            .append(msg).append("\"}");
    }
}
