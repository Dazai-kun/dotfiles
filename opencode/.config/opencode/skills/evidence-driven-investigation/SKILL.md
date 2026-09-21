---
name: evidence-driven-investigation
description: Investigate bugs, data discrepancies, API uncertainty, missing mappings, metric mismatches, and unclear system behavior using reproducible evidence before proposing changes.
---

# Evidence-Driven Investigation

Use this skill when the primary problem is uncertainty about what the system, API, database, data, or code is actually doing.

Typical cases:

- missing IDs or mappings
- unexpected nulls
- metric discrepancies
- unclear or undocumented API behavior
- data present in one system but absent from another
- rows unexpectedly filtered, duplicated, or transformed
- runtime behavior differing from assumptions
- suspected bugs without an established root cause

Do not use this skill merely because a task involves code.

If the desired behavior and cause are already clear, proceed with normal planning or implementation.

## Objective

Reduce uncertainty until there is enough evidence to make a sound decision.

A successful outcome does not require a code change.

Valid outcomes include:

- root cause identified
- hypothesis rejected
- API limitation confirmed
- data issue isolated
- implementation change justified
- no change required
- additional evidence explicitly identified

## Workflow

### 1. Define the observable problem

State what is actually observed.

Prefer measurable statements.

Avoid beginning with an assumed cause.

### 2. Establish a reproducible signal

Find the smallest reliable way to demonstrate the issue.

Examples:

- focused query
- single failing test
- one API request
- one representative record
- one log signature
- one reproducible command

Prefer deterministic evidence over broad inspection.

### 3. Gather authoritative evidence

Prefer direct sources such as:

1. live or reproducible system behavior
2. repository source code
3. authoritative schema or system metadata
4. existing tests
5. first-party documentation
6. stable project documentation
7. secondary sources when necessary

Use project-specific skills when they provide authoritative information.

### 4. Build hypotheses

Separate:

**Confirmed facts**
- directly observed or verified

**Hypotheses**
- plausible but not yet proven

**Unknowns**
- relevant evidence still missing

Never present a hypothesis as a fact.

### 5. Choose a discriminating test

Prefer the cheapest test that most clearly separates competing hypotheses.

Avoid broad scans when a targeted probe can answer the question.

### 6. Iterate until decision-ready

Repeat:

evidence
→ update hypotheses
→ next discriminating test

Stop when additional investigation is unlikely to change the implementation decision.

Do not investigate indefinitely for completeness.

### 7. Synthesize findings

Return a compact summary:

## Problem

What was observed.

## Evidence

The strongest relevant evidence.

## Conclusion

What the evidence supports.

## Remaining uncertainty

Only uncertainty that still materially matters.

## Recommended next step

Examples:

- create implementation plan
- run one additional targeted probe
- update documentation
- no code change required

Do not jump directly from symptoms to implementation.

## Persisting knowledge

Persist expensive reusable findings in the project's established documentation location when one exists.

Do not create a new documentation convention unnecessarily.

Do not persist routine debugging transcripts.

## Guardrails

- Do not modify production behavior during investigation unless explicitly requested.
- Prefer read-only probes.
- Do not expose secrets.
- Do not infer facts that can be inspected directly.
- Do not broaden scope merely because unrelated issues are discovered.
