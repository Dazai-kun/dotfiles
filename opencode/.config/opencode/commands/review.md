---
description: Independently review the current changes against their specification
agent: reviewer
---

Review the current changes.

Specification / plan / task reference (may be empty): $ARGUMENTS

Determine exactly which diff you are reviewing before judging it. Default to the
working tree and staged changes against HEAD. If the reference above points to a
plan or specification file, read it first and treat it as the source of truth for
intended behavior; if it names a base branch or commit range, review that range
instead.

Load and follow the `code-review` skill. Report findings using the reviewer
severity levels, finding format, and output format.
