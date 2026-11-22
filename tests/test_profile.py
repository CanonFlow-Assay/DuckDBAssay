from copy import deepcopy
import unittest

from test_engine import CAT, engine

PROFILE = "parquet-compatibility"
AMOUNT = {"name": "amount", "physical": "INT64", "repetition": "REQUIRED",
          "logical": "DecimalType(scale=4, precision=18)", "precision": 18, "scale": 4,
          "type": "DECIMAL(18,4)", "fieldId": None}
NOTE = {"name": "note", "physical": "BYTE_ARRAY", "repetition": "OPTIONAL",
        "logical": "StringType()", "precision": None, "scale": None, "type": "VARCHAR", "fieldId": None}
GOOD = {
    "baselineSha256": "a" * 64, "candidateSha256": "b" * 64, "baselineSchema": [AMOUNT],
    "candidateSchema": [AMOUNT, NOTE], "baselineRows": 2, "candidateRows": 2, "baselineFooterRows": 2,
    "candidateFooterRows": 2, "baselineOnlyRows": 0, "candidateOnlyRows": 0,
}


def outcomes(value):
    return {item["ruleId"]: item["outcome"] for item in engine.evaluate({"parquet": value}, CAT, PROFILE)}


class ParquetCompatibilityProfile(unittest.TestCase):
    def test_no_unchecked_rules_in_the_profile(self):
        actual = outcomes(deepcopy(GOOD))
        selected = {rule["id"] for rule in CAT["rules"] if PROFILE in rule["profiles"]}
        self.assertEqual(actual, {rule_id: "passed" for rule_id in selected})

    def test_each_rule_has_a_conclusive_negative_control(self):
        for rule, field, value in (
            ("DDBP001", "candidateSchema", [{**AMOUNT, "scale": 2}, NOTE]),
            ("DDBP002", "candidateSchema", [AMOUNT, {**NOTE, "repetition": "REQUIRED"}]),
            ("DDBP003", "candidateFooterRows", 3),
            ("DDBP004", "candidateOnlyRows", 1),
        ):
            with self.subTest(rule=rule):
                sample = deepcopy(GOOD)
                sample[field] = value
                self.assertEqual(outcomes(sample)[rule], "failed")

    def test_empty_duplicate_or_uncompared_scope_remains_untested(self):
        sample = deepcopy(GOOD)
        sample["baselineRows"] = 0
        sample["candidateSchema"] = [AMOUNT, AMOUNT]
        sample["candidateOnlyRows"] = None
        self.assertEqual(set(outcomes(sample).values()), {"untested"})
