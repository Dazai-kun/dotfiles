---
name: grilling
description: Stress-test an ambiguous requirement, plan, or design through focused decision-making before implementation.
---

# Grilling

Use this skill when important decisions remain unresolved before planning or implementation.

Typical cases:

- vague feature requests
- architectural changes
- competing implementation approaches
- unclear requirements
- significant data-model decisions
- API integration design
- meaningful trade-offs
- plans containing hidden assumptions

Do not use this skill merely because a task is complex.

Do not grill decisions already established by repository evidence, documentation, or explicit user requirements.

## Principle

Facts are the agent's responsibility.

Decisions are the user's responsibility.

If a question can be answered by:

- reading the repository
- using Explore
- inspecting project documentation
- using a project-specific authoritative skill
- consulting first-party documentation
- running a safe probe

investigate it instead of asking the user.

Ask the user when the answer represents:

- intent
- preference
- business requirement
- acceptable trade-off
- scope
- risk tolerance
- architectural choice without a clearly dominant answer

## Process

Build a decision tree around the problem.

Start with decisions that other decisions depend on.

Do not ask downstream questions until their prerequisites are resolved.

For each decision:

1. State the decision clearly.
2. Provide relevant evidence or constraints.
3. Present reasonable options.
4. Give a recommended option when appropriate and explain why.
5. Ask the user to decide or correct the recommendation.

Prefer a small number of related questions per round.

Do not dump the entire decision tree on the user at once.

## Use investigation when needed

If a decision depends on an unknown fact, pause that branch and investigate the fact.

Use Explore for repository discovery.

Use `evidence-driven-investigation` when resolving the unknown requires reproducible evidence or hypothesis testing.

Resume the decision tree once the necessary evidence is available.

## Avoid redundant questions

Before asking:

- check whether the user already answered it
- check current session context
- check relevant project documentation
- check whether repository evidence determines the answer

Never ask the user to repeat information already available.

## Recommendations

Do not make the user choose between unexplained options.

When appropriate, recommend an option based on:

- repository conventions
- simplicity
- maintainability
- existing architecture
- available evidence
- stated user goals

Clearly distinguish evidence from judgment.

The user owns the final decision.

## Completion

Continue until remaining unresolved decisions either:

- do not materially affect implementation, or
- are explicitly accepted as implementation-time choices.

Then summarize:

### Goal

What is being achieved.

### Confirmed facts

Relevant facts established through investigation.

### Decisions

Important choices made and their rationale.

### Constraints

Requirements and invariants implementation must preserve.

### Remaining unknowns

Only unresolved items that materially matter.

### Recommended next step

Usually one of:

- investigate
- create implementation plan
- prototype
- proceed with bounded implementation

Do not begin implementation automatically.
