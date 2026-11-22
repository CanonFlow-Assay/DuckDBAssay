"""Observe typed flat Parquet files and their projection using DuckDB 2.0."""

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import duckdb

LIMIT = 4 * 1024 * 1024


def file_identity(path):
    if any(part.is_symlink() for part in (path, *path.parents)) or not path.is_file() or path.stat().st_size > LIMIT:
        raise ValueError("profile requires a local regular Parquet file of at most 4 MiB")
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def argument(path):
    if any(char in str(path) for char in "*?[]"):
        raise ValueError("wildcard filenames are outside the single-file profile")
    return str(path)


def schema(connection, path):
    result = connection.execute("""
SELECT name, type, repetition_type, logical_type, precision, scale, duckdb_type, field_id, num_children
FROM parquet_schema(?) ORDER BY column_id
""", [path]).fetchall()
    if not result or result[0][-1] != len(result) - 1 or any(row[-1] for row in result[1:]):
        raise ValueError("only nonempty flat Parquet schemas are supported")
    keys = ("name", "physical", "repetition", "logical", "precision", "scale", "type", "fieldId")
    return [dict(zip(keys, row[:-1], strict=True)) for row in result[1:]]


def quoted(name):
    return '"' + name.replace('"', '""') + '"'


def collect(baseline, candidate):
    if duckdb.__version__ != "2.0.0":
        raise RuntimeError("profile requires DuckDB 2.0.0")
    baseline, candidate = baseline.absolute(), candidate.absolute()
    hashes = [file_identity(path) for path in (baseline, candidate)]
    operands = [argument(path) for path in (baseline, candidate)]
    config = {"threads": 1, "memory_limit": "192 MiB", "allow_unsigned_extensions": False,
              "allow_community_extensions": False, "autoinstall_known_extensions": False,
              "autoload_known_extensions": False}
    with duckdb.connect(config=config) as connection:
        connection.execute("SET TimeZone='UTC'")
        base, changed = [schema(connection, path) for path in operands]
        count = [connection.execute("SELECT count(*) FROM read_parquet(?)", [path]).fetchone()[0]
                 for path in operands]
        footer = [connection.execute("SELECT num_rows FROM parquet_file_metadata(?)", [path]).fetchone()[0]
                  for path in operands]
        lookup = {item["name"]: item for item in changed}
        differences = [None, None]
        if all(lookup.get(item["name"]) == item for item in base):
            fields = ", ".join(quoted(item["name"]) for item in base)
            compare = (f"SELECT count(*) FROM (SELECT {fields} FROM read_parquet(?) EXCEPT ALL "
                       f"SELECT {fields} FROM read_parquet(?))")
            differences = [
                connection.execute(compare, order).fetchone()[0]
                for order in (operands, list(reversed(operands)))
            ]
    if hashes != [file_identity(path) for path in (baseline, candidate)]:
        raise RuntimeError("Parquet data changed during native observation")
    return {
        "schemaVersion": 1, "product": "duckdb", "version": duckdb.__version__,
        "parquet": {
            "baselineSha256": hashes[0], "candidateSha256": hashes[1], "baselineSchema": base,
            "candidateSchema": changed, "baselineRows": count[0], "candidateRows": count[1],
            "baselineFooterRows": footer[0], "candidateFooterRows": footer[1],
            "baselineOnlyRows": differences[0], "candidateOnlyRows": differences[1],
        },
    }


def fixture(directory):
    baseline = directory / "baseline.parquet"
    candidates = {name: directory / (name + ".parquet")
                  for name in ("compatible", "decimal-drift", "timestamp-drift", "changed-value", "required-field")}
    with duckdb.connect(config={"threads": 1}) as connection:
        connection.execute("SET TimeZone='UTC'")
        rows = ("SELECT * FROM (VALUES (1, 12.5001::DECIMAL(18,4), "
                "TIMESTAMPTZ '2026-01-10 09:20:30.123456-05', 'first'), "
                "(2, -0.0001::DECIMAL(18,4), TIMESTAMPTZ '2026-01-11 00:00:00+05:30', NULL)) "
                "AS t(id, amount, occurred_at, memo)")
        connection.execute("CREATE TABLE fixture AS " + rows)
        projections = {
            baseline: "*",
            candidates["compatible"]: "*, NULL::VARCHAR AS annotation",
            candidates["decimal-drift"]: "id, amount::DECIMAL(18,2) AS amount, occurred_at, memo",
            candidates["timestamp-drift"]: "id, amount, occurred_at::TIMESTAMP AS occurred_at, memo",
            candidates["changed-value"]: "id, (amount + 0.0001)::DECIMAL(18,4) AS amount, occurred_at, memo",
            candidates["required-field"]: "*, 'required'::VARCHAR AS annotation",
        }
        for path, fields in projections.items():
            connection.execute(f"COPY (SELECT {fields} FROM fixture ORDER BY id) TO ? (FORMAT PARQUET)", [str(path)])
    return {name: collect(baseline, candidate) for name, candidate in candidates.items()}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--candidate", type=Path)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--output", type=Path)
    target.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    if bool(args.baseline) != bool(args.candidate):
        parser.error("supply both Parquet operands")
    if args.baseline:
        observations = {"compatible": collect(args.baseline, args.candidate)}
    else:
        with tempfile.TemporaryDirectory(prefix="duckdb-assay-parquet-") as directory:
            observations = fixture(Path(directory))
    result = observations["compatible"]
    if args.output:
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        for stage, specimen in observations.items():
            if stage != "compatible":
                (args.output.parent / f"{stage}.json").write_text(json.dumps(specimen, indent=2) + "\n")
    elif result != json.loads(args.check.read_text()):
        raise RuntimeError("re-executed Parquet observations differ from the declared snapshot")
    print(json.dumps(result, sort_keys=True))
