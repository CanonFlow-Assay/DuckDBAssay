---
name: duckdb-engineering
description: "Build or review DuckDB 2.0 analytical pipelines and embedded/server integrations with explicit data, resource, extension and recovery boundaries."
---

# DuckDB engineering

Inspect the actual engine, binding, extension versions, data formats and execution mode. The researched target is DuckDB 2.0.0 LTS as of 2026-11-16. Preserve an existing project toolchain unless the task needs migration; review format/API/extension compatibility before adopting 2.0 features.

Separate embedded file ownership from Quack/client-server access. Use the mode's documented concurrency and filesystem model. For remote Quack, review authentication, TLS proxying, client/server execution placement and cancellation; a client setting need not control server resource use.

Budget memory, threads, result materialization, spill storage and concurrent jobs together. memory_limit constrains managed memory rather than the entire process. Some operators still exhaust memory; measure skewed inputs and actual process/container peaks. Bound result consumption and define disk-full/cancellation/restart behavior.

Specify schema, decimals, timestamps and nulls, validate join cardinality and reconcile outputs. Use Parquet projection/filter pushdown and measured row-group/partition/file layout. Preserve required ordering when changing insertion-order settings or parallel output.

Treat SQL, relational expressions and extension loading as capabilities with filesystem/network consequences. Bind data and validate paths/identifiers. For untrusted input, use defense-in-depth settings plus appropriate process/OS isolation; signed extensions and locked settings alone are not a sandbox.

Read [engineering decisions](references/best-practices.md) and [source decisions](references/sources.json). Historical/alpha benchmarks provide hypotheses, not guaranteed 2.0 speedups. DuckDBAssay supplies pipeline and untrusted-input snapshot profiles with explicit missing evidence; it does not qualify Quack, S3, spill performance or arbitrary hostile SQL. Run configured tests within the actual task scope and retain their raw outcomes.
