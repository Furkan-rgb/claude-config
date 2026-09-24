# Global Engineering Principles

Preserve intent, understand the system, make sound decisions, and keep the finished system correct and understandable.

## Understandability Is a Requirement

Software that works but can no longer reasonably be understood is not a successful result. For substantial changes, retain a coherent mental model and be able to explain:

- the important domain concepts
- where important behavior lives
- what calls what
- the main execution and data flow
- where important state is owned
- why meaningful abstractions exist
- how the behavior could later be modified

If these become difficult to explain, investigate whether unnecessary complexity was introduced. Developer comprehension is part of done.

## Simplest Adequate Solution

Code generation is cheap. Maintenance and comprehension are not.

Prefer the simplest solution that correctly satisfies the actual requirement. Avoid speculative abstractions, unnecessary interfaces or layers, wrappers around wrappers, generic infrastructure without concrete need, premature extensibility, duplicate concepts, unclear state ownership, excessive indirection, and abstractions without domain meaning.

Complexity must have a concrete justification. Prefer explicit domain names over vague names such as Manager, Handler, Helper, Processor, or generic Service when a meaningful name exists.

## Domain Before Framework

Reason about what the software does rather than organizing everything around framework terminology. Use domain language explicitly and apply Domain-Driven Design pragmatically.

Favor ubiquitous language, explicit concepts, meaningful boundaries, and clear ownership. Do not introduce DDD ceremony without concrete value.

## Understand Before Changing

Before substantial implementation, establish as relevant:

- current behavior
- execution and data flow
- domain concepts and state ownership
- affected boundaries and existing abstractions
- tests, constraints, and similar behavior

Distinguish observed facts, assumptions, risks, and unknowns. Verify assumptions that can reasonably be checked. Do not redesign from guesses.

## Specification Before Planning

For substantial work, establish WHAT should exist before determining HOW to implement it.

A useful specification captures as appropriate:

- problem and desired outcome
- scope, constraints, and non-goals
- requirements and domain concepts
- acceptance criteria and important risks

Specification = WHAT. Plan = HOW. Do not allow implementation decisions to silently redefine requirements.

Permanent specification files are optional. Create durable project documentation when it has lasting value or the project or developer explicitly requires it.

## Scale the Process to the Task

### Small

Task → Implement → Verify

Examples include an obvious local bug, rename, tiny configuration change, straightforward test fix, or simple UI adjustment. Work directly.

### Standard

Analyze → Spec → Plan → Implement → Review → Verify → Simplify

### Architectural, Long-Running, or High-Risk

Deep Analysis → Relevant Expert Consultation → Spec → Architecture → Complexity Check → Plan → Implement → Independent Review → Verify → Simplify → Documentation Reconciliation → Comprehension Check

Scale each stage to the task; do not turn the workflow into ceremony.

## Long-Running Stages

A long-running stage — a training run, a soak, a benchmark on an exclusive device — is owned by a script that runs the stage, its evaluation and its cleanup unattended and exits with a status. Do not poll a log or sleep in a loop waiting for it; start it once as a background task and let the harness's completion notification wake you.

## Scope Discipline

Do not expand scope merely because other improvements are visible. Avoid unrelated refactoring.

Do not add configurability, abstractions, fallbacks, infrastructure, generic systems, defensive machinery, or documentation merely because they might someday be useful.

If implementation exposes a wrong assumption or plan, return to the decision instead of layering workarounds over it.

## Review and Verification

Review asks, “Is this implementation good?” Verification asks, “Did we actually achieve the intended outcome?” Treat them as separate concerns.

Review against the original task, specification, requirements, acceptance criteria, and architecture. Verify with evidence appropriate to the task, such as unit, integration, or end-to-end tests; builds; type checking; linting; static analysis; targeted manual scenarios; and relevant performance or security checks.

Run focused verification first and broaden it when scope or risk justifies it. Avoid repetitive verification once sufficient evidence exists.

For especially consequential milestones — major architecture changes, security-sensitive work, persistence redesign, concurrency, foundational systems, large migrations — a review by a separate model or provider is worth doing. Treat it as a deliberate manual step the developer initiates, not as part of the automatic workflow.

## Simplification Pass

After substantial work is correct, ask, “Now that this works, what complexity is no longer necessary?”

Inspect for dead code, duplicate flows, obsolete abstractions, temporary adapters, forwarding-only layers, unnecessary interfaces, generic helpers without a clear responsibility, and stale compatibility paths. Simplify when doing so improves comprehension without weakening requirements.

## Documentation Reconciliation

Permanent documentation should describe the system that actually exists. When implementation materially changes durable architecture, domain, ADR, or specification documentation, reconcile it. Do not create documentation merely for ceremony.

## Definition of Done

A substantial task is complete when:

- requirements are implemented and acceptance criteria are verified
- important review findings are resolved and relevant checks pass
- architecture and domain boundaries remain coherent
- state ownership is understandable
- unnecessary complexity and temporary artifacts are removed
- durable documentation is accurate where relevant
- you can clearly explain the resulting system and how it can later be changed
