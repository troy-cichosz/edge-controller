# ChatGPT Project Working Rules

This document is the working contract for how ChatGPT and the user develop, verify, document, and recover the AI Legal Edge Platform. It is not the platform architecture specification; enduring platform rules belong in `projectrules.md`. The objective is to preserve enough accurate context for safe continuation, not to maximize documentation length.

## 1. Repository and Branch Workflow

### 1.1 Repository Authority

* The GitHub repositories are the committed reference available to ChatGPT.
* The `public` branch represents the **last known-good ADO-mirrored state** of the repository.
* When the user confirms that the repositories are current, ChatGPT shall treat the current `public` branch as the authoritative baseline for development.
* The ADO/on-prem repositories are not directly accessible to ChatGPT. The user is responsible for ADO integration, builds, deployments, runtime verification, and the ADO → GitHub mirror.
* Branch history must not be used as a substitute for the ADO verification process. A change is not considered successfully implemented merely because it exists in `chatgpt` or `public`.

### 1.2 Branch Roles

* **`public`** — last known-good ADO-mirrored baseline.
* **`chatgpt`** — ChatGPT development branch containing proposed or implemented work for the current development increment.
* ChatGPT shall make repository changes on `chatgpt`, not directly on `public`.
* `public` is not a development workspace.
* The branches must not be treated as interchangeable.
* A change present only on `chatgpt` is proposed/in development, regardless of whether it has been committed.
* A change present on `public` is part of the committed ADO-mirrored baseline, but is considered verified only according to the normal build, deployment, and runtime verification workflow.

### 1.3 Development Baseline

* The normal starting baseline is `public`.
* For an active increment, the user may explicitly designate `chatgpt` as the source of truth. When that happens, use `chatgpt` for that increment rather than treating the older `public` state as authoritative.
* After a completed increment becomes known-good, `public` becomes the new baseline.
* Before the next increment, `chatgpt` should be synchronized, rebased, or reset from the new `public` baseline as appropriate so completed work does not accumulate as obsolete development state.

### 1.4 ADO Verification and GitHub Mirroring

The user controls the ADO/on-prem portion of the workflow:

1. Integrate the approved changes into ADO.
2. Build the affected components.
3. Deploy the resulting artifacts.
4. Verify runtime behavior.
5. Verify relevant failure/recovery behavior where applicable.
6. Mirror the resulting known-good state to GitHub `public`.

The existence of a commit in GitHub does not replace these operational verification steps.

Legacy `chatgpt.md` files are retired and are **not authoritative**. They must not be created, maintained, or used as service/project status or handoff documents. Development state must be maintained in `servicestatus.md` and `sprintstatus.md`; durable project state belongs in the project-level documents defined in Section 5. Any legacy `chatgpt.md` file that remains in a repository is obsolete and should be removed.

### 1.5 ChatGPT Branch Synchronization

After the user confirms an increment is complete and the ADO state has been mirrored to `public`, ChatGPT shall verify the resulting `public` state before beginning the next increment. The `chatgpt` branch should then be synchronized from that baseline as appropriate.

### 1.6 ADO State During Troubleshooting

If the user reports that the local ADO state differs from `public`, the user's reported ADO state takes precedence for operational troubleshooting until the next ADO → GitHub mirror. ChatGPT shall not assume that `public` contains unmirrored ADO changes.

## 2. Development Workflow

The normal development sequence is:

1. **Review the rules before doing substantive work.** At the beginning of every new development increment, and whenever the scope changes materially, review the current `chatrules.md`. If the work can affect an architectural invariant, also review `projectrules.md`.
2. **Establish the current source of truth and baseline.** Determine whether `public` or an explicitly designated `chatgpt` state is authoritative for the increment.
3. **Review the authoritative documentation.** Inspect the applicable project documents and affected service documents before proposing implementation or documentation changes. Do not rely solely on prior conversation context when the repository can be inspected.
4. **Define the intended change.** Establish the architecture, scope, verification requirements, and documentation impact before implementation.
5. **Present substantive proposed changes for confirmation.** Architectural changes, implementation changes, and meaningful documentation restructuring/content changes require user confirmation before commitment.
6. **Implement only the approved change on `chatgpt`.**
7. **Review the resulting code and documentation changes.**
8. The user integrates the approved changes into ADO.
9. ADO builds the affected components.
10. The user deploys the resulting artifacts.
11. Runtime behavior is verified.
12. Relevant failure/recovery behavior is verified where applicable.
13. **Perform the documentation completion audit** described in Section 6.2. Documentation must be updated from verified results, not merely from intended implementation.
14. ADO mirrors the resulting known-good state to GitHub `public`.
15. ChatGPT verifies the resulting `public` baseline before beginning the next increment.

A development increment must not be considered complete merely because code exists, a commit exists, or a build succeeds. Operational completion depends on the verification appropriate to the capability.

## 3. Definition of "All Green"

When the user states **"all green"**, it means:

* the requested changes were implemented;
* the changes were integrated into ADO;
* the affected builds succeeded;
* the resulting artifacts were deployed;
* runtime behavior was verified;
* relevant failure/recovery behavior was verified where applicable;
* documentation was updated as appropriate; and
* the resulting ADO state was mirrored to the GitHub `public` branch.

At that point, ChatGPT may treat the updated `public` branch as the new known-good development baseline. The `public` branch itself is evidence of the mirrored state; the user's ADO build, deployment, and runtime verification establish whether the increment is operationally known-good.

## 4. Repository Recovery

When previous repository content must be recovered:

1. Use repository history and existing branches/commits to recover the actual previous state whenever possible.
2. Do not reconstruct substantive documentation, architecture, project history, or wishlist content from memory when an earlier committed version can be recovered.
3. Preserve the distinction between the stable `public` baseline and current `chatgpt` development work during recovery.
4. Identify and verify recovery changes explicitly before they become part of the `public` baseline.

## 5. Documentation Ownership

Project-level and service-level documents have distinct authoritative responsibilities. Information must be maintained in the document whose purpose best fits it. A document is not updated merely because a feature touched that area; it is updated when information owned by that document changes.

### 5.1 `chatrules.md`

The working contract for ChatGPT and the user. It defines repository/branch workflow, development and verification workflow, documentation lifecycle, documentation ownership, promotion rules, recovery/troubleshooting discipline, communication and confirmation expectations, and other ChatGPT-specific project working rules.

It answers:

> **How do ChatGPT and the user work on this project?**

### 5.2 `projectrules.md`

Enduring platform architectural and engineering invariants that implementation must respect.

It answers:

> **What rules must the platform architecture continue to obey?**

A workflow instruction belongs in `chatrules.md`, not `projectrules.md`. An enduring platform constraint belongs in `projectrules.md`, not `chatrules.md`.

### 5.3 `projectoverview.md`

The high-level platform map: purpose, architecture, domain concepts, service roles, maturity, major boundaries, and summarized direction.

It answers:

> **What is the platform and how is it organized?**

It is not the detailed project history, current sprint tracker, service implementation manual, or future-capability backlog.

### 5.4 `projectstatus.md`

The authoritative highest-level project development record. It contains significant project milestones, major development state changes, project-altering decisions, and historical context necessary to understand how the platform reached its current state.

It answers:

> **What significant development state has the project reached, and what major decisions or milestones produced it?**

It must not become a detailed task list, service-specific sprint log, troubleshooting notebook, or speculative future-capability list.

### 5.5 Project `sprintstatus.md`

The live platform sprint-lifecycle tracker. It contains the current platform sprint objective, active work, completed work for the current increment, verification requirements, blockers/deferred work, immediate next actions, and handoff.

It answers:

> **What platform work are we actively doing now, and what must happen next?**

It is not the long-term project history.

### 5.6 `wishlist.md`

Desired future capabilities, ideas, or deferred scope that has not been promoted into active development.

It answers:

> **What do we want to build later?**

A wishlist item must not be documented as current capability merely because it is desired or architecturally discussed.

### 5.7 `envinfo.md`

Temporary ChatGPT-facing development-environment and deployment reference information needed to reconstruct the current development/lab environment.

It answers:

> **What temporary environment facts do we need to know to work effectively right now?**

It is not a permanent architecture or service-status record and is ultimately removed when no longer needed.

### 5.8 Service `servicestatus.md`

The authoritative current development phase and maturity record for one service. It contains verified capabilities, current phase, current limitations, remaining service-level work, and the service's current position in the platform lifecycle.

It answers:

> **What is this service actually capable of today, at what verified maturity, and what remains at the service level?**

It must not become a detailed sprint log, implementation diary, or speculative feature list.

### 5.9 Service `sprintstatus.md`

The live development tracker for one service. It contains the current sprint objective, active work, completed work for the current increment, verification requirements, blockers/deferred work, immediate next actions, and handoff.

It answers:

> **What are we actively doing to move this service forward, and what must be verified next?**

It is the service-level equivalent of the project sprint tracker and must not replace `servicestatus.md`.

### 5.10 Service `README.md`

Permanent service documentation for someone who needs to understand or operate the service. It covers purpose, platform role, architecture, interfaces, configuration, data/evidence behavior, operation, troubleshooting, and relevant implementation/build information.

It answers:

> **How does this service work and how is it operated?**

The README describes actual service behavior and contracts; it does not replace sprint or maturity tracking.

### 5.11 `evidencearchitecture.md`

The authoritative common evidence architecture. It defines shared Evidence, Observation, Event, Timeline, temporal, provenance, integrity, attestation, manifest, custody, derivative, reconstruction, and technical-boundary concepts that span services.

It answers:

> **What common evidence model must participating services integrate with?**

It is not a service implementation manual or current sprint tracker.

### 5.12 Repository placement

Project-level documents live in `edge-controller` because it is the master service and project management repository. They describe the entire AI Legal platform, not `edge-controller` specifically.

Service `servicestatus.md`, `sprintstatus.md`, and `README.md` live in their owning service repositories.

### 5.13 Status versus sprint distinction

The distinction must remain explicit:

| Document | Stability | Primary question |
|---|---|---|
| `projectstatus.md` | Relatively stable; historical | What significant project state/history has been established? |
| project `sprintstatus.md` | Actively changing | What platform work is happening now? |
| service `servicestatus.md` | Relatively stable; maturity | What verified service state exists now? |
| service `sprintstatus.md` | Actively changing | What service work is happening now? |

When information describes **current work**, it belongs in `sprintstatus.md`. When it describes **verified maturity or significant established state**, it belongs in `servicestatus.md` or `projectstatus.md` as appropriate. When it describes **how the service works**, it belongs in the README.

### 5.14 Documentation is authoritative by ownership

If two documents contain overlapping information, the document whose purpose owns that information is authoritative. The other document should use a concise cross-reference rather than maintaining a competing detailed copy.

If documents contradict one another, stop and resolve the contradiction against the actual repository/runtime evidence before continuing substantive work. Do not silently choose the more convenient statement.


## 6. Documentation Preservation

1. **Preserve substantive documentation by default.** Do not rewrite a long document into a short summary merely because a shorter document looks cleaner.
2. **Do not remove detail solely to reduce line count.** Remove information only when it is demonstrably obsolete, contradictory, duplicated without value, or intentionally superseded.
3. **Do not delete wishlist items merely because they are not currently scheduled.**
4. Preserve historical failures, recovery procedures, architectural decisions, and lessons learned when they remain useful to future development.
5. When a new fact supersedes an old fact, update the old statement rather than deleting the surrounding historical context without explanation.
6. Avoid duplicating the same detailed implementation material across repository documents. Keep information in the document whose purpose best fits it and reference the relationship where useful.

## 6.1 Documentation Update Rules by Development Effort

Documentation updates must follow ownership rather than a blanket "update every MD file" rule.

| Development effort | Required documentation review/update |
|---|---|
| Platform-wide architectural model or cross-service evidence/temporal/provenance change | Review `projectrules.md`, `evidencearchitecture.md`, `projectoverview.md`, project `sprintstatus.md`, and affected service docs. Update each only when its owned information changes. |
| Service implementation or interface change | Affected service `README.md` and service `sprintstatus.md`; update `servicestatus.md` when verified maturity/capability/remaining work changes; update project docs only when platform-level information changes. |
| Successful feature/integration milestone | Affected service `README.md` and `sprintstatus.md`; update `servicestatus.md` when maturity changes; update project `sprintstatus.md` for cross-service/platform handoff; update `projectstatus.md` only when the milestone is significant at project level. |
| Current development environment/deployment change | `envinfo.md`; affected service README/status only when the service contract or verified operational state changes. |
| Future capability or deferred idea | `wishlist.md`; promote to `sprintstatus.md` only when it becomes active work. Do not represent it as current capability. |
| Project-level restructuring/documentation ownership change | `chatrules.md` and the affected ownership/map documents; preserve substantive content and audit for contradictions. |
| Troubleshooting/failure/recovery discovery | Affected service README/status/sprint as appropriate; project docs only if the finding changes platform-level architecture, status, or history. Preserve useful diagnostic facts without turning hypotheses into facts. |
| Enduring architectural invariant established or changed | `projectrules.md`; update `projectoverview.md`/`evidencearchitecture.md` only where their owned concepts or high-level map also change. |

### Required update sequence after a verified development increment

Use this sequence as a decision process, not as a requirement to modify every file:

1. **Affected service README:** record service behavior, interface, configuration, operational, evidence, or troubleshooting facts that were actually verified.
2. **Affected service `sprintstatus.md`:** update the current sprint state, completed increment, verification result, blockers, and handoff.
3. **Affected service `servicestatus.md`:** update only if verified phase, maturity, capability set, limitation, or remaining service-level work changed.
4. **`evidencearchitecture.md`:** update only if the increment establishes or changes a common Evidence/Observation/Event/Timeline/temporal/provenance/integrity concept.
5. **`projectrules.md`:** update only if an enduring architectural or engineering invariant is established or changed.
6. **Project `sprintstatus.md`:** update when work is cross-service, changes the active platform handoff, or materially changes current platform work.
7. **`projectstatus.md`:** update only for a significant project milestone, project-altering decision, major development-state transition, or historical fact worth preserving at project level.
8. **`projectoverview.md`:** update only when the high-level platform map, role, maturity, architecture summary, or direction changes.
9. **`envinfo.md`:** update only for current temporary environment/deployment facts.
10. **`wishlist.md`:** update only when future scope is added, clarified, deferred, or promoted.

Do not update a document merely to make it mention the same completed feature. Prefer one authoritative location and concise cross-references elsewhere.

## 6.2 Documentation Completion Audit

Before an increment can be treated as complete, ChatGPT must perform a documentation audit against the actual verified result.

The audit must answer:

1. What changed in the implementation or architecture?
2. What behavior was actually verified?
3. What failed, remained unverified, or is still deferred?
4. Which document owns each resulting fact?
5. Does the affected README describe the verified service behavior?
6. Does the applicable `sprintstatus.md` reflect the current lifecycle state and handoff?
7. Does `servicestatus.md` still accurately describe verified maturity?
8. Did the common evidence architecture change?
9. Did an enduring architectural invariant change?
10. Did the project-level sprint state change?
11. Is the change significant enough for `projectstatus.md`?
12. Did the high-level project map change?
13. Did environment facts change?
14. Did future scope change?
15. Does any existing documentation now contain an obsolete, contradictory, or misleading statement?

The audit must update or explicitly leave unchanged each applicable document based on ownership. "No change required" is a valid result when the document's authoritative information did not change.

A feature must not be promoted from sprint work to verified service/project status solely because it was implemented. Promotion requires the verification appropriate to that capability.

The final documentation state must distinguish:

- implemented versus verified;
- operational versus experimentally demonstrated;
- current capability versus future capability;
- active work versus deferred work;
- architectural intent versus implemented behavior;
- observed facts versus hypotheses.

### Documentation promotion lifecycle

Future scope normally progresses through:

`wishlist.md`
   |
   | promoted into active work
   v
`sprintstatus.md`
   |
   | implemented and appropriately verified
   v
`servicestatus.md` / `projectstatus.md`
   |
   | enduring architectural invariant established
   v
`projectrules.md`

This is a lifecycle, not an automatic requirement to copy the same text between documents. Information should be moved or summarized into its new authoritative location as its state changes.

## 7. Verification Standards

### 7.1 Rules Before Work

Before substantive work begins, review `chatrules.md`. When architecture or enduring constraints may be affected, review `projectrules.md` as well. If the work spans services, review the relevant project-level documentation and affected service documentation.

### 7.2 Source Before Assumption

Inspect the actual current source and documentation before inventing routes, models, behavior, or project state. Do not rely on memory when the repository contains authoritative material.

### 7.3 Incremental Verification

Verify each end-to-end capability before adding another abstraction layer. Do not expand the implementation on top of an unverified foundation.

### 7.4 Runtime Completion

A feature is not complete merely because code exists, a commit exists, or a build succeeds. Deployed components must demonstrate the expected runtime behavior, with relevant cross-service and failure/recovery behavior verified where applicable.

### 7.5 Failure and Recovery Verification

When failure behavior matters to the capability, verify the failure mode and recovery behavior rather than treating a restart or successful retry as proof of a permanent fix. Record useful diagnostic observations for future troubleshooting.

### 7.6 Verification Determines Status Promotion

Implementation does not automatically advance `servicestatus.md` or `projectstatus.md`.

The appropriate status document may advance only when the evidence needed for the claimed state exists. Where failure/recovery behavior is part of the capability, that behavior must be verified before documenting the capability as complete.

### 7.7 Documentation Reflects Verified State

Documentation must describe what was actually verified. Do not convert an observation, temporary recovery, or hypothesis into a permanent root-cause claim without evidence.

### 7.8 Contradiction Check

Before completing an increment, compare the changed facts against the relevant existing documentation. Correct obsolete or contradictory statements in their authoritative location rather than adding a second statement that creates competing truths.

## 8. Troubleshooting and Evidence Discipline

1. A restart may be documented as a recovery action when runtime evidence shows that it restored operation, but it must not be called the root cause or permanent fix unless demonstrated.
2. Preserve diagnostic timing measurements, logs, failure modes, and recovery observations when they materially affect future troubleshooting.
3. Distinguish verified facts from hypotheses and planned work.
4. When evidence is relevant to a technical conclusion, preserve the source and context needed to reproduce or reassess that conclusion.

## 9. Review Discipline

### 9.1 Mandatory Rules Review

At the beginning of every new development increment, and whenever the scope changes materially, ChatGPT must review the current `chatrules.md` before making implementation, architecture, status, or documentation decisions.

If the proposed work appears to conflict with an existing rule, ChatGPT must identify the conflict before proceeding. A rule must not be silently overridden because a different approach appears more convenient.

### 9.2 Mandatory Authority Review

After reviewing `chatrules.md`, ChatGPT must inspect the authoritative documents relevant to the work:

- `projectrules.md` for architectural invariants;
- `projectoverview.md` for high-level platform map/direction;
- `projectstatus.md` for significant project state/history;
- project `sprintstatus.md` for current platform work;
- `evidencearchitecture.md` for common evidence/temporal/provenance concepts;
- `wishlist.md` when future/deferred scope is relevant;
- `envinfo.md` when environment/deployment facts matter;
- affected service `README.md`;
- affected service `servicestatus.md`;
- affected service `sprintstatus.md`.

Not every document requires modification. The requirement is to consult the documents whose information can materially affect the work.

### 9.3 Repository-State Verification

Verify that the documentation being relied upon matches the current repository state. If the repository contains newer or contradictory information, resolve that discrepancy before continuing.

### 9.4 No Conversation-Only Continuation

Do not continue substantive development solely from prior conversation context when the current repository state can be inspected.

Prior conversation may provide useful context, but repository source, verified runtime results, and authoritative project documentation take precedence according to the repository and verification rules.

### 9.5 Completion Review

At the end of an increment, perform the Documentation Completion Audit in Section 6.2 before treating the increment as complete.

The objective is to resume and finish work from documented, verified state rather than assumptions.

## 10. Communication and Change Confirmation

1. **Routine inspection and verification do not require confirmation.** ChatGPT may inspect repositories, review code/docs, compare states, and report findings without waiting for approval.
2. **Substantive proposed changes require confirmation before commitment.** This includes architectural changes, implementation changes, and meaningful documentation restructuring or content changes.
3. **After the user confirms the proposed change, ChatGPT may commit the approved change to `chatgpt`.**
4. **ADO integration, builds, deployment, runtime verification, and ADO → GitHub mirroring remain user-controlled steps.**
5. If the user reports a verified result, ChatGPT should use that result as the current operational fact while still distinguishing it from assumptions or unverified repository state.

## 11. New Chat Handoff

When the user indicates that the current development effort will continue in a new chat (for example, **"let's continue in a new chat"**), ChatGPT shall first perform the applicable documentation completion check for the current increment.

Before ending the current chat, ChatGPT shall:

1. Review the current development state against the authoritative repository documentation and the verified results available for the current increment.
2. Update applicable authoritative documentation when the current increment has established a fact, changed verified status, changed the active handoff, or otherwise requires a documentation update under Section 6.
3. Respect the existing confirmation requirements in Section 10. Documentation changes that constitute substantive or meaningful changes still require user confirmation before commitment. The new-chat request itself does not override that requirement.
4. Verify the relevant current `public` repository state when the user has completed and mirrored an increment, in accordance with Sections 1–3.
5. Provide a concise new-chat handoff containing:
   - current project and affected-service development state;
   - the active or next development increment;
   - completed and verified work relevant to continuation;
   - applicable architectural invariants and settled decisions that must be preserved;
   - authoritative repositories/branches and their baseline state;
   - known blockers, unverified behavior, deferred work, and important limitations;
   - the files changed during the current handoff effort, with direct repository links when useful; and
   - a ready-to-paste opening message for the new chat.
6. Explicitly distinguish implemented from verified, current capability from future scope, and architectural intent from implemented behavior.
7. Do not create or rely on a `chatgpt.md` handoff document. The handoff is a communication artifact; authoritative project/service state remains in the documents defined by Section 5.

This rule supplements the existing development, documentation, verification, branch, and confirmation rules. It does not replace, weaken, or override them.
