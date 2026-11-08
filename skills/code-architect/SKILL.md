---
name: code-architect
description: Design or evolve software architecture when a task spans modules, services, APIs, data flows, or important quality attributes.
---

# Code Architect

## Workflow
1. **Discover before designing.** Inspect the repository tree, entry points, manifests, runtime versions, existing architecture notes, conventions, tests, and deployment configuration. Read the relevant implementation rather than inferring behavior from names.
2. **Clarify constraints.** Identify the user-visible outcome, compatibility requirements, supported platforms, latency/scale needs, data sensitivity, operational limits, and what must remain unchanged. Ask only for a decision that blocks a safe design.
3. **Map the system.** Trace the current request/data flow across boundaries. Record ownership, dependencies, persistence, external services, trust boundaries, and failure modes.
4. **Compare options.** Prefer the smallest design that satisfies the requirements. Explain meaningful alternatives and trade-offs; avoid introducing abstractions, services, dependencies, or configuration without a concrete benefit.
5. **Plan evolution.** Define interfaces, invariants, migration/backward-compatibility strategy, rollback path, observability, and test seams before implementation.
6. **Validate the design.** Check that each requirement maps to a component and a test. Revisit security, concurrency, resource bounds, and partial failure.
7. **Communicate.** Separate facts observed in the repository from assumptions and proposals. State decisions, consequences, open questions, and a staged implementation plan.

## Design principles
- Preserve established project conventions unless there is a clear reason to change them.
- Keep modules cohesive and dependencies directed; put policy at the appropriate boundary.
- Validate untrusted input at system boundaries and enforce authorization server-side.
- Make state transitions and error behavior explicit; design idempotency where retries are possible.
- Treat secrets, personal data, filesystem access, subprocesses, and network access as security boundaries.
- Prefer additive, reversible migrations. Never silently discard user data.
- Consider observability without logging credentials or sensitive payloads.

## Deliverable
Provide a concise architecture summary, component responsibilities, key interfaces/data flow, risks and mitigations, migration/rollback notes, and a verification plan. Do not claim a design is implemented until code and tests prove it.
