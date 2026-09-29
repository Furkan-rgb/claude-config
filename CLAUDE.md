# Global Engineering Principles

## Understandability Is a Requirement

Software that works but can no longer be understood is not done. For substantial changes, be able to explain the domain concepts, where behavior and state live, the main flow, and why each abstraction exists; if you can't, look for complexity you introduced.

## Simplest Adequate Solution

Prefer the simplest solution that correctly meets the actual requirement: simplest for the whole system to understand, not the smallest diff. A special case, duplicate, or workaround that leaves the cause in place is not simpler; if the cause is outside your scope, report it rather than patch around it. Add no speculative abstractions, layers, interfaces, generic infrastructure, configurability, fallbacks, defensive code, or documentation without a concrete present need.

## Domain Before Framework

Name things in the domain's language, not Manager, Handler, Helper, Processor, or Service, when a domain name exists.

## Understand Before Changing

Before substantial changes, establish current behavior, flow, state ownership, and the affected boundaries and tests. Separate observed facts from assumptions, verify what you reasonably can, and do not redesign from guesses.

## Scope Discipline

Do not expand scope merely because other improvements are visible. Avoid unrelated refactoring.

If implementation exposes a wrong assumption or plan, return to the decision instead of layering workarounds over it.

## Verification

Verify with the evidence the task needs, focused first, broadening only when scope or risk justifies it; stop once the evidence is sufficient.

## Long-Running Stages

A long-running stage — a training run, a soak, a benchmark on an exclusive device — is owned by a script that runs the stage, its evaluation and its cleanup unattended and exits with a status. Do not poll a log or sleep in a loop waiting for it; start it once as a background task and let the harness's completion notification wake you.
