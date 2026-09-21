# Global Working Method

## Scope

- This file applies to every repository and carries reusable working method only.
- Repository `AGENTS.md` files add domain rules: architecture, build/test commands, framework conventions, project safety, and documentation conventions.
- Keep project paths, schemas, commands, and credentials out of this file.

## Built-in Agents

- Use the built-in `Plan`, `Build`, `Explore`, and `General` agents as provided.
- Do not replace or wrap them with new agents, commands, or override system prompts. Extend their behavior with skills and instruction files.
- Add a new agent only for a genuinely new workflow role that skills cannot provide, such as the read-only `reviewer` subagent.

## Facts and Decisions

- Facts are the agent's responsibility. Establish them with evidence.
- Decisions are the user's responsibility: intent, preference, business requirements, acceptable trade-offs, scope, risk tolerance, and architectural choices without a clearly dominant answer.
- When a question can be answered by reading the repository, using Explore, inspecting project documentation, loading an authoritative project skill, consulting first-party documentation, or running a safe probe, investigate it instead of asking the user.
- Ask the user when no available evidence can settle the question. Do not guess.

## Task Classification

Before substantial work, classify the task by its actual uncertainty and scope.

- **Spike**: primarily discovery, reproduction, feasibility, root-cause investigation, or proving an assumption.
- **Bounded change**: desired behavior is reasonably clear and affects a limited part of the system.
- **Architectural change**: changes shared patterns, contracts, data models, or multiple parts of the system.

Do not force small changes through an architectural workflow.

Escalate the classification if investigation reveals broader impact.

## Investigation Quality

For uncertainty-heavy work:

- Define the observable problem before proposing causes.
- Establish the smallest reproducible signal.
- Gather direct evidence before forming implementation conclusions.
- Separate confirmed facts, hypotheses, and unknowns.
- Prefer the cheapest test that best distinguishes competing hypotheses.
- Avoid speculative fixes while the relevant behavior can still be verified.
- Persist expensive reusable findings in the project's established documentation location when one exists.

## Planning Quality

A good implementation plan must be grounded in evidence from the current repository and relevant system behavior.

Before finalizing a substantial plan:

- inspect the relevant implementation
- inspect the closest comparable pattern when useful
- use Explore for repository discovery when additional tracing is needed
- reuse evidence already established earlier in the session
- identify the concrete components likely to change
- describe behavioral changes and invariants rather than line-by-line edits
- identify validation seams for important behaviors
- distinguish confirmed facts from assumptions
- leave unresolved questions only when they materially affect implementation

Plans should normally include:

1. Goal
2. Current behavior / evidence
3. Proposed changes
4. Validation
5. Material unresolved questions, if any

## Explore Findings

When Explore is used by Plan or Build, return synthesized evidence rather than a search transcript.

Prefer:

- relevant files and symbols
- current control/data flow
- closest comparable implementation
- confirmed constraints and invariants
- contradictions or important unknowns

Do not narrate routine search steps or dump every file inspected.

## Skill Selection

Investigation resolves facts. Grilling resolves decisions. Do not use `grilling` to ask factual questions, and do not use `evidence-driven-investigation` to make business decisions.

```text
Spike
├── usually Explore
└── evidence-driven-investigation when uncertainty requires testing

Bounded change
├── inspect current implementation
├── grill only if material requirements remain ambiguous
└── concise Plan → Build

Architectural change
├── Explore
├── investigation for unknown facts
├── grilling for unresolved decisions
├── design / Plan
└── Build
```

Target mental model:

```text
Explore       "What does the repository contain?"
Investigation "What is actually true?"
Grilling      "What do we want?"
Plan          "Given the facts and decisions, how should we implement it?"
Build         "Implement and validate it."
```

## Testing and Validation

Validation is required, but persistent test artifacts are not required for every change.

Prefer the smallest validation method that provides sufficient confidence.

### Persistent tests

Create or modify persistent test files when at least one of the following applies:

- the repository already has tests covering the affected behavior;
- the change introduces reusable logic with meaningful regression risk;
- the change fixes a bug that could reasonably recur;
- the behavior contains important edge cases that should remain protected;
- the project explicitly requires tests for this type of change.

When an existing relevant test can be extended, prefer extending it over creating a new test file.

### Ad-hoc validation

For one-off investigation and implementation validation, prefer disposable methods such as:

- existing test commands;
- inline Python or shell commands;
- SQL queries;
- temporary files outside the repository;
- `/tmp`;
- existing project tooling;
- direct inspection of representative inputs and outputs.

Examples include API response inspection, ETL data checks, SQL validation, mapping verification, schema inspection, and debugging.

Do not create permanent test files, fixtures, mock payloads, debug scripts, sample outputs, or validation artifacts solely to prove that the current task works.

If temporary files must be created inside the repository, remove them before completing the task.

### Before adding a new test file

Ask:

> Does this test provide ongoing regression protection that will be useful after the current implementation is complete?

If no, validate the behavior without adding a persistent test artifact.

### Completion

Do not claim that a change is validated merely because no persistent test was created.

Report the validation method actually used, for example:

- existing tests passed;
- SQL results were compared;
- API behavior was verified;
- representative data was processed successfully;
- static/type/lint checks passed;
- temporary validation was performed and artifacts were removed.

Testing strategy should be proportional to the risk and nature of the change rather than maximizing the number of test files.

## Code Review

After non-trivial implementation work, validate it with the `reviewer` subagent
before considering the task complete. The reviewer is independent and read-only.

Provide it with:

- the implementation plan, requirements, or acceptance criteria
- the relevant git diff or change range
- repository instructions
- relevant test results

Do not pass it the implementation agent's reasoning unless that reasoning is part
of the approved specification. Fresh context reduces anchoring.

The reviewer performs two independent passes: specification compliance and
technical quality. It reports findings as BLOCKER, IMPORTANT, or MINOR.

Fix BLOCKER and IMPORTANT findings before completion, then run one focused
re-review. MINOR findings may be deferred. Do not loop review and fix
indefinitely; additional rounds require an explicit request.

Invoke it with `/review [plan-or-spec-reference]`, or by asking the primary agent
to use the `reviewer` subagent.

Task-size flow:

```text
Small change (minor fix, localized refactor, config update)
└── implement → test → review once

Normal feature
└── plan/spec → implement → tests → review → fix important → re-review

Large change (new integration, migration, cross-module feature)
└── plan → implement by milestone → optional milestone review
   → final whole-change review
```

Do not review every individual file or trivial non-code edit.

The reviewer model is configuration, not architecture. Configure it with the
`model` field in `agents/reviewer.md` (or a `/review` command `model:` field),
using `provider/model#variant`. When unset, the reviewer inherits the calling
session's model. Planning, implementation, and review may each use any model.
