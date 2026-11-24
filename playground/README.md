# DuckDBAssay playground

The wrapper evaluates a checked-in DuckDB 2.0.0 settings snapshot with the `pipeline` policy. The source suite also contains separate Parquet compatibility cases.

Run the source commands from the repository root with Python 3.
[Native fixture setup](../docs/native.md)

```sh
python3 playground/run.py
```

The v2 receipt preserves command arguments, exits, and raw logs for
readiness, catalogue explanations, source tests, the showcase verification,
and the provisional scan control. The scan control expects
`Inconclusive` with exit `2`. The wrapper propagates a failed or
incomplete showcase and refuses a contradictory receipt and process exit.

For the native receipt alone, run each command independently.

```sh
PYTHONPATH=src python3 -m duckdb_assay scan examples/snapshot.json --policy examples/policy.json
PYTHONPATH=src python3 -m duckdb_assay verify examples/snapshot.json --policy examples/policy.json
```

The example policy has an empty `requiredCommands` list. Both commands report `Inconclusive` with exit `2` for this fixture. The repository's native smoke or Parquet qualification commands produce their own evidence.

Install the pinned wheel into `.venv` using the native fixture setup. Use
the environment interpreter for both the qualification and its replay.

```sh
.venv/bin/python eng/qualify-profile.py --out artifacts/Parquet-qualification
.venv/bin/python playground/run.py --policy artifacts/Parquet-qualification/policy.json \
  --snapshot artifacts/Parquet-qualification/snapshot.json
```
