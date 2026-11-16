# Research and admission decisions

Reviewed 2026-11-16 for duckdb 2.0.0. Community articles identify hypotheses, incidents and test cases. Exact product semantics come from primary documentation and executed native fixtures. No article, popularity score or benchmark ratio automatically admits a blocking rule.

| Source | Kind | Decision |
|---|---|---|
| [D-SEC](https://duckdb.org/docs/2.0/operations_manual/securing_duckdb/overview) | primary | SQL and relational expressions can access capabilities; settings are defense in depth, not a sandbox. |
| [D-EXT](https://duckdb.org/docs/2.0/operations_manual/securing_duckdb/securing_extensions) | primary | Native extensions carry process privileges; unsigned/custom repository decisions require explicit trust. |
| [D-CONFIG](https://duckdb.org/docs/2.0/configuration/overview) | primary | Native settings export via duckdb_settings; explicit resource settings. |
| [D-CONCUR](https://duckdb.org/docs/2.0/connect/concurrency) | primary | Choose embedded single-process ownership versus supported Quack access; do not generalize old multi-process limitations to all 2.0 modes. |
| [D-OOM](https://duckdb.org/docs/current/guides/performance/oom) | primary | Buffer-manager limit is not whole-process memory isolation. |
| [D-PARQUET](https://duckdb.org/docs/2.0/data/parquet/tips) | primary | Projection/filter pushdown, row-group layout and partitioning need workload measurements. |
| [D-REDDIT](https://www.reddit.com/r/DuckDB/comments/1g8higx/memory_limitsspillover/) | community | Concurrent resource competition motivates explicit budgets; historical connection/process descriptions are version-qualified. |
| [D-MEDIUM](https://medium.com/arcesium-engineering-blog/query-faster-query-smarter-our-move-to-duckdb-and-what-we-learned-c935128e80bc) | community | Parquet staging and parallel output are candidates to measure, not promised universal speedups. |
| [D-MEMORY](https://medium.com/@kirill.fedorov2112/your-duckdb-memory-limit-is-not-an-isolation-boundary-03ea51302304) | community | Hypothetical/AI-assisted article is explicitly low authority; its memory/spill concerns are checked against official documentation. |
| [D-SUBSTACK-QUACK](https://ramonactruta.substack.com/p/measuring-quack-duckdbs-new-client) | community | Client/server parallelism and execution placement motivate separate measurement. Reported ratios are not generalized to 2.0 workloads. |
| [D-SUBSTACK-IO](https://performancede.substack.com/p/duckdb-20-and-s3-file-read-performance) | community | Alpha benchmark is version/workload specific. No guaranteed speedup, global CLI replacement or curl-to-shell installer is imported. |
| [D-MEMORY-AUTHOR](https://www.duckdb.org/2024/07/09/memory-management) | primary | Engine-author explanation supports managed-memory versus process-memory distinction. |
| [D-ASYNC-IO](https://duckdb.org/2026/07/31/asynchronous-io) | primary | Verify eligible formats and actual execution path; do not promise async I/O benefits for every format based on an alpha benchmark. |

The complete conceptual checklist is in [best practices](best-practices.md). Only the finite catalogue is implemented as executable profile checks. Missing inputs remain untested; contextual recovery, performance, migrations and security behavior require declared external tests. These sources are linked and synthesized in original wording rather than copied in full.
