# Global Working Method

## Scope

- This file applies to every repository and carries reusable working method only.
- Repository `AGENTS.md` files add domain rules: architecture, build/test commands, framework conventions, project safety, and documentation conventions.
- Keep project paths, schemas, commands, and credentials out of this file.

## Built-in Agents

- Use the built-in `Plan`, `Build`, `Explore`, and `General` agents as provided.
- Do not add replacement system prompts for them. Extend behavior with skills and instruction files instead of new agents or command wrappers.

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
