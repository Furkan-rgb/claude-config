---
name: lead-playbook
description: How to run a substantial engineering task end to end when you own it: scaling the process, specification before planning, review and verification, simplification, and documentation reconciliation. Load when you own an engineering task beyond a small, obvious change, not when carrying out work another agent delegated to you.
---

# Lead Playbook

## Scale the Process to the Task

Small, obvious changes need no spec, plan, or separate review.

**Standard:** Analyze → Spec → Plan → Implement → Review → Verify → Simplify

**Architectural, long-running, or high-risk:** Deep Analysis → Relevant Expert Consultation → Spec → Architecture → Complexity Check → Plan → Implement → Independent Review → Verify → Simplify → Documentation Reconciliation → Comprehension Check

Scale each stage to the task; do not turn the workflow into ceremony.

## Specification Before Planning

Establish what should exist before how to build it: problem and outcome, scope and non-goals, requirements and domain concepts, acceptance criteria, risks. Do not let implementation decisions silently redefine requirements. Write the spec to a file only when it has lasting value or the project or developer asks for one.

## Review and Verification

Review (is the implementation good?) and verification (did we achieve the outcome?) are separate checks; review against the original task, specification, acceptance criteria, and architecture.

For especially consequential milestones (major architecture, security, persistence, concurrency, foundational systems, large migrations), tell the developer a review by another provider's model is worth running; the developer starts it, not you.

## Simplification Pass

Once substantial work is correct, remove what it no longer needs — dead code, duplicate flows, temporary adapters, stale compatibility paths, forwarding-only layers — without weakening requirements.

## Documentation Reconciliation

When the work materially changes durable architecture, domain, ADR, or specification docs, update them to match what exists.
