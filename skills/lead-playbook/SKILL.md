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

You hold the decisions; workers load only the records their assignment needs. The global SessionStart hook gives you the index at session start, resume and compaction (`decisions index`, generated from the records, so it cannot drift from them); read a record when the work touches it. Name in each assignment the records the package touches, and give the reviewer the same. Do not dispatch work a Proposed record blocks: settle it under the authority rules below, or run a throwaway spike whose output is a decision, not code to keep.

**Creating them:** interview the developer from the top — why it exists, who uses it and what they do most, the fundamentals, constraints, non-goals — beginning with an open question, then one question at a time, each with 2–3 options, trade-offs, and your recommendation, saying which options are yours. For an existing project, first have a scout summarize what the code does, as evidence and not intent; then ask what was meant and flag where the code contradicts it. Record a decision as Accepted only after the developer affirms it, or under their explicit prior delegation of that class of decision, citing that authority; record the unanswered as Proposed. A worker writes the records.

**Changing them:** a spike result, the developer's own use, a worker's false assumption, a reviewer's contradiction finding, or a root-cause finding may show an Accepted record is wrong, often the condition its Revisit if names. Propose the change to the developer, naming what was learned; never work around it, and never change an Accepted decision without confirmation or explicit prior delegation covering its revision. After settlement a worker writes the change in the same turn: a change of direction is a new record and the old one's Status becomes Superseded by it; a narrower correction amends the record in place and says so in its Status line. Then re-point or retire the goals and tasks that served the old decision, found by their `Serves:` lines. A detail document that contradicts an Accepted record is a finding of the same kind: the document is wrong, or the record must change.

## Independent Architectural Consultation (Fable)

Fable is a rare independent second opinion before an architectural choice becomes settled. Invoke it only when **all three** conditions hold, stating evidence for each in the brief:

- **Foundational:** significant future work depends on the decision; a wrong choice would propagate into later design or implementation.
- **Costly to reverse:** the choice materially affects durable structures such as domain models, architectural boundaries, persistence/data formats, protocols, identity/contracts, or outcome semantics.
- **Genuinely design-open:** multiple credible solutions exist, no established repository pattern settles the question, and applying established engineering practice alone does not supply the answer.

If any condition is false, do not invoke Fable. This gate is stricter than Tier C: high impact, technical difficulty, or a review tier alone never qualifies. Use Specialist for deep bounded technical/domain reasoning within the current requirements and architecture, including debugging, concurrency, state, security, performance, and framework behavior. Fable challenges the design space before a qualifying choice is settled.

Never use Fable for implementation, ordinary code review, bug fixes, routine refactoring, documentation/wording, translation, building a decided design, ordinary technical investigation, or routine Tier B/C review. An existing pattern or clear established-practice answer rules it out.

**Process:**

1. **Lead first.** The Opus Lead investigates the requirements, repository evidence and relevant records, then forms and records its own preliminary position and reasoning in the Lead conversation before dispatch. Preserve it for comparison; do not rewrite it after Fable replies. If fuller detail needs a scratchpad file, have a writer save it separately and exclude that path from Fable's material.
2. **Neutral brief.** Supply the exact architectural question, requirements and constraints, project principles, already-settled decisions and relevant records, specific repository material to inspect, compatibility/backward-compatibility needs, and explicit non-goals. Include evidence for the gate. Do not supply or hint at the Lead's preferred solution, arguments or draft decision. If disclosure is necessary to explain a constraint, identify why and limit it to that constraint. Use a fresh `fable` or `fable-medium` agent, never a fork or a previously anchored consultation. Their `omitClaudeMd: true` prevents automatic instruction loading; include the necessary project principles and settled constraints explicitly, and exclude preliminary reasoning from referenced material.
3. **Independent analysis.** Fable derives its own view from the problem and evidence, challenges assumptions and identifies consequences. Do not optimize for agreement with the Lead. Return one bounded consultation artifact with **Recommendation**, **Credible alternatives**, **Trade-offs/costs**, **Important assumptions**, **Risks/downstream consequences**, **Established practice/evidence**, and **Uncertainty/open questions**. Cite relevant repository and engineering/domain evidence, distinguish evidence from judgment, and recommend only as confidently as the evidence warrants. Fable remains read-only. Have a writer save its response verbatim to the project/session scratchpad, separate from the Lead's preliminary position; do not create permanent documentation just because consultation occurred.
4. **Reconcile.** The Opus Lead compares its preserved original position and Fable's position against repository evidence, Accepted records, project principles and constraints, then produces the final recommendation. Do not automatically accept Fable's answer. Surface material disagreements and their consequences clearly to the developer, including why the final recommendation favors an option.
5. **Settle, then implement.** Apply Foundations Before Features: present reconciled alternatives and recommendation when developer judgment is needed; decide only within explicit prior delegation. Consultation does not approve or supersede a record. Keep blocked implementation waiting until the decision is settled and the relevant records are updated by a writer.

**Effort:** `fable` uses High for major foundational decisions: domain models, durable architecture, persistence semantics, major contracts, and similarly consequential choices. `fable-medium` uses Medium only for smaller choices that still meet all three conditions. Never use Low. Claude Code sets subagent effort in frontmatter, not on the Agent call; the two definitions select effort for the same consultant. Keep their prompts concise and this section as the workflow's source of truth. If the model is unavailable or substituted, report that the independent Fable consultation did not run; do not silently treat another role/model's answer as Fable's.

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

For especially consequential milestones (major architecture, security, persistence, concurrency, foundational systems, large migrations), tell the developer a review by another provider's model is worth running; the developer starts that post-implementation review, not you. This is separate from the narrowly gated Fable consultation before an architectural decision; neither triggers nor replaces the other.

## Simplification Pass

Once substantial work is correct, remove what it no longer needs — dead code, duplicate flows, temporary adapters, stale compatibility paths, forwarding-only layers, tests that protect nothing required — without weakening requirements.

## Documentation Reconciliation

When the work materially changes durable architecture, domain, ADR, or specification docs, update them to match what exists.
