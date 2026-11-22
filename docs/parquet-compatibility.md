# Flat Parquet compatibility profile

The parquet-compatibility profile uses DuckDB 2.0.0 to compare one
baseline Parquet file with one candidate file. Existing fields retain
their physical and logical types, decimal precision and scale,
timestamp semantics, field IDs and repetition metadata. An added field
must be optional. Footer counts must match real scans of both files,
and the old projection must have equal multiset contents in both
directions.

~~~sh
python3 eng/qualify-profile.py --out artifacts/parquet-qualified
python3 eng/native_smoke.py --profile parquet-compatibility \
  --baseline baseline.parquet --candidate candidate.parquet --output artifacts/snapshot.json
~~~

The first command writes and reads a real DuckDB fixture. It passes the
optional addition and detects changed decimal scale, changed timestamp
semantics, changed values and a required addition. The packaged verifier
re-executes the compatible native fixture and retains the raw receipt.
The second command collects observations for a specified local file pair.
Use the emitted observations with a policy naming parquet-compatibility
and bind the two files and the replay command. The initial file scope is
flat schema, one regular local file per input, at most 4 MiB each.
An incompatible schema leaves the value comparison untested.

- [DuckDB Parquet metadata](https://duckdb.org/docs/2.0/data/parquet/metadata)
- [Parquet logical types](https://parquet.apache.org/docs/file-format/types/logicaltypes/)
