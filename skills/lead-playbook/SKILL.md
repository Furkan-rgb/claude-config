---
name: lead-playbook
description: How to run a substantial engineering task end to end when you own it: scaling the process, the project design doc and goals, specification before planning, review and verification, simplification, and documentation reconciliation. Load when you own an engineering task beyond a small, obvious change, not when carrying out work another agent delegated to you.
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

A long-lived project — goal-driven work spanning sessions — has one short design doc, owned by the developer: What it is, Decided (fundamentals and invariants), Open (questions that block dependent work), Not doing. Propose one when such a project lacks it. It lives at `docs/design.md`, imported with `@docs/design.md` from the project-root CLAUDE.md, so every session and worker loads it and it survives compaction. It states only current decisions, edited in place; git holds the history. Where it exists, do not dispatch feature work that depends on an Open or undecided fundamental: settle it with the developer, or run a throwaway spike whose output is a decision, not code to keep.

**Creating it:** interview the developer from the top — why it exists, who uses it and what they do most, the fundamentals, constraints, non-goals — beginning with an open question, then one question at a time, each with 2–3 options, trade-offs, and your recommendation, saying which options are yours. For an existing project, first have a scout summarize what the code does, as evidence and not intent; then ask what was meant and flag where the code contradicts it. Record a decision only after the developer affirms it; park the unanswered as Open. A worker writes the file and adds the import.

**Changing it:** a spike result, the developer's own use, a worker's false assumption, or a root-cause finding may show a Decided item is wrong. Propose the change to the developer, naming what was learned; never work around it, and never edit Decided unconfirmed. After confirmation a worker edits the doc in the same turn, and you re-point or retire the goals and tasks that traced to it. When a goal completes, ask the developer one question: did we learn anything that changes Decided or Open?

## Second Fix, Stop

When a second fix lands on the same behavior, dispatch a specialist for the root cause and the design question before any further fix.

## Goals and Roadmap

A goal is an outcome, not a bucket, derived from the design doc; the first goals are its fundamentals. Goals in order are the roadmap: detail only the next goal and keep later ones to one line. On a board with goals, create or dispatch no task without one: attach it to one, propose a new goal to the developer, or ask whether the task is wanted.

## Review and Verification

Review (is the implementation good?) and verification (did we achieve the outcome?) are separate checks; review against the original task, specification, acceptance criteria, and architecture.

Verification is one fast command (tests, type-check, lint), recorded in the project's CLAUDE.md with a time budget. A test earns its place only by protecting a behavior the task or design doc requires, or a bug that happened. What needs human judgment, such as game feel, goes to the developer explicitly.

For especially consequential milestones (major architecture, security, persistence, concurrency, foundational systems, large migrations), tell the developer a review by another provider's model is worth running; the developer starts it, not you.

## Simplification Pass

Once substantial work is correct, remove what it no longer needs — dead code, duplicate flows, temporary adapters, stale compatibility paths, forwarding-only layers, tests that protect nothing required — without weakening requirements.

## Documentation Reconciliation

When the work materially changes durable architecture, domain, ADR, or specification docs, update them to match what exists.
