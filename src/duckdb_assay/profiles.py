"""Finite flat Parquet compatibility predicates for a declared file pair."""

import re

COLUMNS = {"name", "physical", "repetition", "logical", "precision", "scale", "type", "fieldId"}
TYPES = ("REQUIRED", "OPTIONAL")


def schema(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 256:
        raise ValueError("expected bounded nonempty flat schema evidence")
    typed = {}
    for item in value:
        if not isinstance(item, dict) or set(item) != COLUMNS:
            raise ValueError("incomplete Parquet column metadata")
        name = item["name"]
        if not isinstance(name, str) or not name or name in typed or item["repetition"] not in TYPES:
            raise ValueError("expected unique named flat fields and repetition metadata")
        if any(not isinstance(item[key], str) or not item[key] for key in ("physical", "type")):
            raise ValueError("missing physical or DuckDB type")
        if item["logical"] is not None and not isinstance(item["logical"], str):
            raise ValueError("invalid logical type metadata")
        if any(item[key] is not None and type(item[key]) is not int for key in ("precision", "scale", "fieldId")):
            raise ValueError("invalid Parquet precision, scale or field ID")
        typed[name] = item
    return typed


def retained(value):
    baseline = schema(value["baselineSchema"])
    candidate = schema(value["candidateSchema"])
    return all(candidate.get(name) == column for name, column in baseline.items())


def nullable_additions(value):
    baseline = schema(value["baselineSchema"])
    candidate = schema(value["candidateSchema"])
    return all(column["repetition"] == "OPTIONAL"
               for name, column in candidate.items() if name not in baseline)


def observed_counts(value):
    hashes = (value["baselineSha256"], value["candidateSha256"])
    if any(not isinstance(item, str) or not re.fullmatch(r"[a-f0-9]{64}", item) for item in hashes):
        raise ValueError("expected two file byte identities")
    counts = [value[key] for key in ("baselineRows", "candidateRows", "baselineFooterRows", "candidateFooterRows")]
    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("invalid native row counts")
    if counts[0] == 0:
        raise ValueError("empty baseline cannot qualify a read-back")
    return len(set(counts)) == 1


def same_rows(value):
    counts = [value[key] for key in ("baselineOnlyRows", "candidateOnlyRows")]
    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("two native multiset comparison counts required")
    return counts == [0, 0]


CHECKS = {"retained": retained, "nullable-additions": nullable_additions,
          "observed-counts": observed_counts, "same-rows": same_rows}
