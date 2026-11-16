# DuckDB 2.0 engineering decisions

Baseline reviewed on 2026-11-16: DuckDB 2.0.0 LTS. Pin engine, client and native extension compatibility for reproducibility. A new language binding or extension can have a different release/ABI lifecycle from the core engine.

## Choose an execution mode

Separate embedded database ownership from 2.0's Quack/client-server path. Do not generalize older embedded multi-process write limitations to every server deployment. For embedded persistent files, use the supported process/concurrency model and a suitable local filesystem; do not treat an NFS/shared file as a safe multi-writer service. Test transaction-conflict retries and shutdown with the actual topology.

For Quack, review the pinned protocol/client/server capabilities. Keep the server loopback-bound with the documented TLS reverse-proxy pattern for remote exposure. Testing-only external-hostname options are not a production security plan. Put tokens in the existing credential mechanism, and test unauthorized requests, TLS identity, cancellation and server-side resource ownership. Quack is guidance only in this initial Assay, not a qualified network adapter.

## Resource ownership

Set a workload memory budget, threads, spill directory and spill capacity explicitly for the pipeline profile. Account for the host application, result objects, native extensions and allocations outside the buffer manager. Multiple processes do not coordinate their independent memory budgets merely because each uses an 80% default. Connections sharing an engine and independent processes are different cases.

Measure peak process/cgroup memory, temporary-space growth, tail runtime and concurrency under skewed data. A memory limit is not a sandbox or a guarantee every operator spills. Large list/string aggregation and combinations of blocking operators can still exhaust memory. Bound query/result lifetime, fetch incrementally where supported, and avoid materializing an enormous Python result with fetchall.

Do not import fixed GB-per-thread ratios as hard rules. Thread reduction can improve a memory-constrained workload and degrade another. Spill storage needs ownership, available capacity, cleanup and a failure/restart contract. A low memory budget can move the failure to disk-full rather than solve it.

## Data and Parquet contracts

Specify source types, decimal scale, timestamps, nulls, encoding and schema evolution. Auto-detection is useful for exploration but is not a durable interchange schema. Preserve identifier text and leading zeros where required.

Check join cardinalities, duplicate/null keys, unmatched records and conserved totals before optimizing. Sort nested children deterministically when the output contract requires it. Disabling insertion-order preservation does not remove a business requirement for order.

Use projection/filter pushdown and representative EXPLAIN plans. EXPLAIN ANALYZE executes work. Choose file/row-group size, partitioning, compression and PER_THREAD_OUTPUT from measured access patterns and the downstream artifact contract. Avoid millions of tiny files, excessive partition cardinality and a universal row-group setting. Match named output files/manifest membership when parallel output changes file layout.

Stage outputs and verify counts/schema/digests before publishing a completion marker. Atomic rename and crash durability are separate; object-store commit semantics differ from a local filesystem. Restart only from an identified source/schema snapshot and validated completed artifacts.

## Security and 2.0 changes

Treat SQL and relational filter expressions as code with filesystem/network implications. Bind data values and validate paths/identifiers. Extensions run with process privileges. Signed extensions establish publisher/integrity relationships, not general safety. For a trusted pipeline, select required signed extensions deliberately; do not impose the untrusted profile on a legitimate external-data workflow.

For untrusted embedded input, disable unsigned/community/automatic extensions and external access, then lock configuration as defense in depth. Establish separate process/OS/network/resource isolation appropriate to the threat model. An agent must not describe these settings as a hostile-SQL sandbox.

Review VARIANT behavior, asynchronous I/O eligibility, triggers and custom parser/extension trust when adopting 2.0 features. An alpha benchmark showing one format/query speedup does not guarantee every 2.0 path is asynchronous or faster. Measure pinned versions, formats, cold/warm state and server/client execution placement under equal budgets.

The initial Assay checks five pipeline-profile or eight untrusted-profile settings (10 distinct rules across both). It audits supplied evidence; native tests demonstrate small local semantics and two defensive boundaries. Quack, S3, real spill performance, all extensions and arbitrary concurrent workloads remain unqualified. See sources.json for source decisions, including Substack alpha/protocol caveats.
