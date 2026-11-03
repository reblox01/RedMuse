# Report

## Executive summary

One paragraph: what was tested, what was found, and the overall posture.

## Scope and coverage

- Target:
- Scope in:
- Scope out:
- Mode: quick or deep
- Budgets used: probes, wall time, teams
- Phases run:
- Classes probed:
- Classes not probed, and why:
- Run outcome: complete or partial

## Findings

Ranked critical, high, medium, low, info. One section per finding:

- Title, severity, endpoint, parameter, CWE.
- Impact and proof summary.
- Fix.
- CVE fields when the finding came from a CVE intel record: vuln id,
  fixed version, cve status, exploit selected.

## CVE intel

- Shortlist table: vuln id, applicability, fixed version, class,
  probe selected or reason for none.
- Checked: fingerprints queried, with version and source per item.
- Skipped: patched records, unknown-version records, and
  unconfirmed candidates, each with its reason.
- Source status: OSV and NVD ok, skipped, or error, and whether
  the CVE check completed. An incomplete check is stated, never
  hidden behind "no known vulnerabilities".

## Unvalidated

Records that could not be reproduced, with the reason each one stayed
unvalidated.

## Probed but clean

Classes probed with nothing found, and what was tried per class.

## Ensemble and coverage matrix

- Merged findings: which candidate records merged, and the
  confirmed_by list per merged finding.
- Confidence: score and band per finding.
- Coverage matrix: one row per class, one column per assigned
  skill, marked probed, found, clean, or not probed.
- Single coverage classes: classes probed by exactly one skill.
- Gaps: classes with no assigned skill, listed as gaps, never as
  clean.

## Retest

After fixes, one line per fixed finding: fixed, still open, or changed.
