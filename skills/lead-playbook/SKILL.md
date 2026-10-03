---
name: lead-playbook
description: How to run a substantial engineering task end to end when you own it: scaling the process, the project's decision records and goals, specification before planning, review and verification, simplification, and documentation reconciliation. Load when you own an engineering task beyond a small, obvious change, not when carrying out work another agent delegated to you.
---

# Lead Playbook

## Scale the Process to the Task

Small, obvious changes need no spec, plan, or separate review.

**Standard:** Analyze → Spec → Plan → Implement → Review → Verify → Simplify

**Architectural, long-running, or high-risk:** Deep Analysis → Relevant Expert Consultation → Spec → Architecture → Complexity Check → Plan → Implement → Independent Review → Verify → Simplify → Documentation Reconciliation → Comprehension Check

Scale each stage to the task; do not turn the workflow into ceremony.

## Specification Before Planning

Establish what should exist before how to build it: problem and outcome, scope and non-goals, requirements and domain concepts, acceptance criteria, risks. Do not let implementation decisions silently redefine requirements. Write the spec to a file only when it has lasting value or the project or developer asks for one.

## Foundations Before Features

A long-lived project — goal-driven work spanning sessions — records its fundamental decisions as decision records, owned by the developer: one file per decision, `docs/decisions/NNNN-<slug>.md`, made with `~/.claude/skills/lead-playbook/decisions new "<title>"` from the template beside it. A record is its decision's only home, with its context, options, reasons and evidence (board items, `#42`) at full precision; every other document, a game design document, a spec or research, cites it by id (`ADR-0013`) and never restates it. Its Status is Proposed, Accepted, Superseded by a newer record, or Rejected. A Proposed record is an open question, and its Blocks line names what cannot proceed until it is decided. What the project is and what it is not doing are records too. Propose records when such a project lacks them.

You hold the decisions; workers do not load them. The global SessionStart hook gives you the index at session start, resume and compaction (`decisions index`, generated from the records, so it cannot drift from them); read a record when the work touches it. Name in each assignment the records the package touches, and give the reviewer the same. Do not dispatch work a Proposed record blocks: settle it with the developer, or run a throwaway spike whose output is a decision, not code to keep.

**Creating them:** interview the developer from the top — why it exists, who uses it and what they do most, the fundamentals, constraints, non-goals — beginning with an open question, then one question at a time, each with 2–3 options, trade-offs, and your recommendation, saying which options are yours. For an existing project, first have a scout summarize what the code does, as evidence and not intent; then ask what was meant and flag where the code contradicts it. Record a decision as Accepted only after the developer affirms it; record the unanswered as Proposed. A worker writes the records.

**Changing them:** a spike result, the developer's own use, a worker's false assumption, a reviewer's contradiction finding, or a root-cause finding may show an Accepted record is wrong, often the condition its Revisit if names. Propose the change to the developer, naming what was learned; never work around it, and never change an Accepted decision unconfirmed. After confirmation a worker writes the change in the same turn: a change of direction is a new record and the old one's Status becomes Superseded by it; a narrower correction amends the record in place and says so in its Status line. Then re-point or retire the goals and tasks that served the old decision, found by their `Serves:` lines. A detail document that contradicts an Accepted record is a finding of the same kind: the document is wrong, or the record must change.

## Shaping the Roadmap

Derive goals from the decision records with the developer once they hold the fundamentals, before any task exists.

- A Proposed record that blocks dependent work becomes an early spike goal; its done-condition is that record Accepted.
- Cut each goal as a vertical slice: when it is done, something can be used, played, or measured end to end. A layer is not a goal.
- Order by risk and dependency: what could invalidate the design, or what most other work rests on, goes first.
- Title each goal `M<n> <done-condition>`; the number is its place in the roadmap. Its description begins with a `Serves:` line naming the records it derives from (`Serves: ADR-0013, ADR-0020`).
- Propose the draft whole, as one-line goals with your ordering reasons. Have a specialist critique it against the records for bucket goals, unverifiable done-conditions, missing dependencies, and ordering errors, and bring the findings to the developer. Create milestones only after the developer affirms the roadmap.

## Second Fix, Stop

When a second fix lands on the same behavior, dispatch a specialist for the root cause and the design question before any further fix.

## Goals and Roadmap

A goal is an outcome, not a bucket, derived from the decision records; the first goals are the fundamentals. Goals in order are the roadmap: detail only the next goal and keep later ones to one line. On a board with goals, create or dispatch no task without one: attach it to one, propose a new goal to the developer, or ask whether the task is wanted.

When a goal completes, reconcile before starting the next: ask the developer whether anything learned changes a record, Accepted or Proposed, or meets a Revisit if; re-check the remaining goals against the records, retiring, re-pointing, adding, or re-ordering them (`ledger milestone rename`) with the developer; then detail the next goal into exits and tasks. `ledger close` says when an item completes its goal.

## Review and Verification

Review (is the implementation good?) and verification (did we achieve the outcome?) are separate checks; review against the original task, specification, acceptance criteria, and architecture.

Verification is one fast command (tests, type-check, lint), recorded in the project's CLAUDE.md with a time budget. A test earns its place only by protecting a behavior the task or an Accepted record requires, or a bug that happened. What needs human judgment, such as game feel, goes to the developer explicitly.

For especially consequential milestones (major architecture, security, persistence, concurrency, foundational systems, large migrations), tell the developer a review by another provider's model is worth running; the developer starts it, not you.

## Simplification Pass

Once substantial work is correct, remove what it no longer needs — dead code, duplicate flows, temporary adapters, stale compatibility paths, forwarding-only layers, tests that protect nothing required — without weakening requirements.

## Documentation Reconciliation

When the work materially changes durable architecture, domain, ADR, or specification docs, update them to match what exists.
