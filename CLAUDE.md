# Global Engineering Principles

## Understandability Is a Requirement

Software that works but can no longer be understood is not done. For substantial changes, be able to explain the domain concepts, where behavior and state live, the main flow, and why each abstraction exists; if you can't, look for complexity you introduced.

## Simplest Adequate Solution

Prefer the simplest solution that correctly meets the actual requirement: simplest for the whole system to understand, not the smallest diff. A special case, duplicate, or workaround that leaves the cause in place is not simpler; if the cause is outside your scope, report it rather than patch around it. Add no speculative abstractions, layers, interfaces, generic infrastructure, configurability, fallbacks, defensive code, or documentation without a concrete present need. Prefer locality: a change should touch few files, behind narrow boundaries.

## Domain Before Framework

Name things in the domain's language, not Manager, Handler, Helper, Processor, or Service, when a domain name exists.

## Scope Discipline

Do not expand scope merely because other improvements are visible. Avoid unrelated refactoring.

If implementation exposes a wrong assumption or plan, return to the decision instead of layering workarounds over it.
