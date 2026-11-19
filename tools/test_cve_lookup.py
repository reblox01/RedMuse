#!/usr/bin/env python3
"""Regression tests for tools/cve_lookup.py OSV range aggregation.

Standard library only. Run from the repo root with either:

    python3 tools/test_cve_lookup.py
    python3 -m unittest discover -s tools -p "test_*.py" -v

The tests call osv_applicability directly on fabricated OSV
vulnerability records, so no network is needed. They cover the
GPT 7 bug: a later non-applicable range overwrote an earlier
applicable one, so a version inside the first of several disjoint
affected ranges was reported not-applicable.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cve_lookup  # noqa: E402


def vuln(*range_events):
    """Build a minimal OSV vuln record from one events list per range."""
    return {
        "affected": [
            {"ranges": [{"events": events} for events in range_events]},
        ],
    }


class TestOsvApplicability(unittest.TestCase):
    def test_disjoint_ranges_version_in_first_only(self):
        # Fixed in 2.0, reintroduced in 3.0, fixed in 4.0. Version 1.5
        # is inside the first range only. The old per-range overwrite
        # reported this not-applicable because the second range did
        # not cover it.
        record = vuln(
            [{"introduced": "1.0"}, {"fixed": "2.0"}],
            [{"introduced": "3.0"}, {"fixed": "4.0"}],
        )
        applicable, fixed = cve_lookup.osv_applicability("1.5", record)
        self.assertEqual(applicable, "applicable")
        self.assertEqual(fixed, "2.0")

    def test_disjoint_ranges_version_in_second_only(self):
        record = vuln(
            [{"introduced": "1.0"}, {"fixed": "2.0"}],
            [{"introduced": "3.0"}, {"fixed": "4.0"}],
        )
        applicable, _ = cve_lookup.osv_applicability("3.5", record)
        self.assertEqual(applicable, "applicable")

    def test_disjoint_ranges_version_in_neither(self):
        record = vuln(
            [{"introduced": "1.0"}, {"fixed": "2.0"}],
            [{"introduced": "3.0"}, {"fixed": "4.0"}],
        )
        applicable, _ = cve_lookup.osv_applicability("2.5", record)
        self.assertEqual(applicable, "not-applicable")

    def test_version_below_introduced_in_every_range(self):
        record = vuln(
            [{"introduced": "1.0"}, {"fixed": "2.0"}],
            [{"introduced": "3.0"}, {"fixed": "4.0"}],
        )
        applicable, _ = cve_lookup.osv_applicability("0.9", record)
        self.assertEqual(applicable, "not-applicable")

    def test_unfixed_second_range_covers(self):
        record = vuln(
            [{"introduced": "1.0"}, {"fixed": "2.0"}],
            [{"introduced": "3.0"}],
        )
        applicable, _ = cve_lookup.osv_applicability("3.5", record)
        self.assertEqual(applicable, "applicable")

    def test_version_exactly_at_fixed_is_not_applicable(self):
        record = vuln([{"introduced": "1.0"}, {"fixed": "2.0"}])
        applicable, _ = cve_lookup.osv_applicability("2.0", record)
        self.assertEqual(applicable, "not-applicable")

    def test_version_exactly_at_introduced_is_applicable(self):
        record = vuln([{"introduced": "1.0"}, {"fixed": "2.0"}])
        applicable, _ = cve_lookup.osv_applicability("1.0", record)
        self.assertEqual(applicable, "applicable")

    def test_non_numeric_version_needs_confirmation(self):
        record = vuln([{"introduced": "1.0"}, {"fixed": "2.0"}])
        applicable, fixed = cve_lookup.osv_applicability("1.0-beta", record)
        self.assertEqual(applicable, "needs-confirmation")
        self.assertEqual(fixed, "2.0")

    def test_no_affected_entries_needs_confirmation(self):
        applicable, fixed = cve_lookup.osv_applicability("1.5", {})
        self.assertEqual(applicable, "needs-confirmation")
        self.assertIsNone(fixed)

    def test_commit_hash_range_gives_no_usable_bound(self):
        record = vuln(
            [{"introduced": "abc123"}, {"fixed": "def456"}],
        )
        applicable, _ = cve_lookup.osv_applicability("1.5", record)
        self.assertEqual(applicable, "needs-confirmation")

    def test_fixed_version_is_first_fixed_seen(self):
        record = vuln(
            [{"introduced": "1.0"}, {"fixed": "2.0"}],
            [{"introduced": "3.0"}, {"fixed": "4.0"}],
        )
        _, fixed = cve_lookup.osv_applicability("5.0", record)
        self.assertEqual(fixed, "2.0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
