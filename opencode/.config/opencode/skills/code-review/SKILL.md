---
name: code-review
description: Independently review a completed implementation against its specification and repository standards, then report findings by severity. Use when reviewing changes, verifying that a plan was implemented, or re-reviewing after fixes.
---

# Code Review

## Purpose

Independently validate an implementation against its specification and repository
standards. Produce concrete, evidence-backed findings. Do not modify files.

## Inputs

- implementation specification (plan, requirements, task description, issue, or
  acceptance criteria)
- git diff or change range
- repository instructions
- relevant tests and test results

If a specification is missing, review against the current task description,
acceptance criteria, and repository instructions. Do not fabricate missing
requirements.

## Procedure

1. Understand the requested behavior.
2. Inspect repository rules (`AGENTS.md`, including nested files).
3. Determine and inspect the diff.
4. Perform the specification-compliance pass.
5. Perform the technical-quality pass.
6. Inspect the tests.
7. Validate suspected issues with repository evidence.
8. Classify findings using the reviewer severity levels.
9. Produce the structured report.

## Explore order

Start from the diff, not the whole repository.

1. Read repository `AGENTS.md` / relevant instructions.
2. Read the implementation plan/spec.
3. Inspect the git diff.
4. Inspect changed files.
5. Inspect directly related dependencies.
6. Inspect relevant tests.
7. Expand exploration only when needed to validate a finding.

You may inspect files touched by the diff, functions imported by changed code,
related schema/model definitions, existing implementations of the same pattern,
tests for affected behavior, repository instructions, and migration dependencies.

Do not perform broad repository exploration without a concrete reason. This
reduces token usage, preserves focus, and avoids unrelated redesign discussions.

Do not treat the absence of newly created test files as a defect by itself. Evaluate whether the implementation was adequately validated and whether persistent regression coverage provides meaningful ongoing value.

## Diff selection

Know exactly which diff you are reviewing. Support:

- current working tree
- staged changes
- branch vs base branch
- specific commit range

Default to the working tree plus staged changes against `HEAD`. Use read-only git
commands (`git diff`, `git diff --staged`, `git status`, `git log`, `git show`,
`git merge-base`, `git rev-parse`). If the caller specified a range, use it.

## Pass 1 — specification compliance

Check:

- Was every required behavior implemented?
- Were acceptance criteria satisfied?
- Were architectural decisions preserved?
- Was anything explicitly requested omitted?
- Was unrelated scope added?
- Did implementation behavior diverge from the specification?
- Were assumptions introduced that contradict the requirements?

## Pass 2 — technical quality

Check:

- correctness
- edge cases
- regression risk
- error handling
- data integrity
- maintainability
- repository conventions
- test quality
- unnecessary complexity

## Test review

Review tests, do not merely confirm they exist.

- Do tests exercise the changed behavior?
- Would the test fail if the implementation were incorrect?
- Are important failure cases covered?
- Are boundary conditions tested?
- Are mocks hiding real behavior?
- Was implementation written narrowly to satisfy a superficial test?
- Are important regressions untested?

Do not demand exhaustive tests for trivial code. Scale scrutiny to risk.

## Domain checklists

Apply only the sections relevant to the task.

### API integrations

pagination, authentication handling, HTTP errors, timeouts, retry behavior, rate
limits where relevant, response validation, missing fields, unexpected nulls,
date boundaries, API-version assumptions, partial responses.

### ETL

idempotency, duplicate prevention, incremental loading, backfill behavior, rerun
behavior, partial failure behavior, transaction boundaries, data loss, schema
evolution, NULL handling, type conversions, timezone handling.

### Airflow

task dependencies, retry configuration, timeouts, catchup, start_date behavior,
execution/logical date semantics, XCom misuse, dynamic task behavior, task
idempotency, failure propagation, resource cleanup.

### PostgreSQL / SQL

join cardinality, accidental row multiplication, NULL semantics, incorrect
filters, transaction safety, constraints, indexes when materially relevant,
migration backward compatibility, destructive operations, upsert behavior,
conflict handling, data types.

### Data mapping

identifier consistency, mapping completeness, fallback behavior, unknown values,
duplicate mappings, many-to-one assumptions, one-to-many assumptions,
normalization, case sensitivity.

## Evidence rules

- Reference concrete files and line numbers.
- Separate confirmed facts from hypotheses.
- Validate a suspected issue against repository evidence before reporting it.
- Prefer the cheapest check that confirms or rejects a suspected problem.

## Finding classification

Distinguish a bug, a requirement mismatch, a useful improvement, and a personal
preference. Only the first three normally appear as findings. Use the severity
levels and finding format defined in the reviewer agent.

## Re-review

After fixes:

1. Verify previous BLOCKER and IMPORTANT findings were resolved.
2. Inspect the new diff introduced by the fixes.
3. Check for regressions.
4. Do not repeat resolved findings.
5. Report newly introduced problems.

## Output

Produce the report format and status mapping defined in the reviewer agent.
