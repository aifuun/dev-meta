---
name: dm-arch-design
description: This skill should be used when designing or adjusting product architecture. It defines two orthogonal constraints — human architecture-design norms and AI execution boundaries — over the same structure (humans set boundaries, AI fills internals). Use it to land the AI collaboration discipline of docs/06 (contract-read-only), docs/07 (observability), and docs/08 (small-batch iteration) onto the concrete "shape of architecture".
---

# dm-arch-design — AI-Assisted High-Cohesion Low-Coupling Architecture Design

Define the human architecture-design norms and the AI execution boundaries as two constraints over the same structure: humans set boundaries, AI fills internals. Reference this skill when creating or adjusting product architecture, to land the AI collaboration discipline of docs/06 (contract-read-only), docs/07 (observability), and docs/08 (small-batch iteration) onto the "shape of architecture".

## Responsibility Boundary

| Responsibility | Owner |
|----------------|-------|
| Define architecture principles and AI guardrails | ✅ This skill |
| Module boundary / Interface / DTO design | ✅ This skill (output lands in docs/06 contract SSOT) |
| Anti-corruption test generation | Delegate dm-dev-tf (per docs/06 & 08) |
| Module internal implementation | Delegate dm-dev-tf (per docs/08 three-batch) |
| Version plan decomposition | Delegate dm-plan-ver (plan decomposable into single-file batches) |

## When to Use

- User says "design the architecture"
- User says "plan module boundaries"
- User says "restructure the code"
- User says "do high-cohesion low-coupling split"
- User says "generate AI guardrails / .cursorrules / CLAUDE.md"

## Core Concepts

### Dual AI-Collaboration Constraints

This skill defines two orthogonal constraints over the same structure:

- **Human architecture-design norms**: unidirectional layering, high cohesion low coupling, minimal-exposure Facade, contract-first — humans set boundaries and interaction contracts.
- **AI execution boundaries**: fill implementation within boundaries, refuse cross-layer/cross-module violations, advance at single-file / single-function granularity (see docs/08).

### Four Architecture Principles

| Principle | Norm (human) | AI execution standard (AI) |
|-----------|--------------|----------------------------|
| **Unidirectional Layering (Clean Architecture)** | Strictly follow `Domain → Use Case → Adapter → Infrastructure` dependency direction; no reverse or cross-layer calls | Refuse to write cross-layer direct access (e.g. forbid Controller talking to DB directly) |
| **High Cohesion Low Coupling** | Split sub-modules by business domain (bounded context), not only by technical component | Keep each module's code within the size AI's context can efficiently understand (see docs/08) |
| **Minimal Exposure (Facade)** | Each sub-module exposes only through a unified `Facade` / API; all internals private | When generating features, prefer querying existing exposed interfaces; forbid calling private functions directly |
| **Contract-First** | Module interaction must define Interface, DTO, and event structures before implementation | Before implementing, must feed the Interface to AI as Context (see docs/06 §2.8 contract-read-only) |

### Core Mechanisms

- **Module concealment & interface narrowing**: each sub-module provides a single `index` / `facade` file at root; except for types/functions explicitly exported by the Facade, other sub-folders (`internal/`, `services/`) are not public. Echoes docs/08 §2.2: only the core algorithm layer needs tests; UI/views skip TDD — private implementations inside the Facade are done by AI in small batches, humans only review boundaries.
- **Dedicated communication module (decouple cross-module interaction)**: synchronous communication uses Mediator or lightweight RPC proxy, forbidding hard-coded mutual references; asynchronous communication uses an **Event Bus** — the producer only publishes domain events (e.g. `OrderCreatedEvent`), the consumer subscribes and processes independently, achieving zero direct dependency.
- **Observability built-in (no separate stack)**: key paths inside a module must carry structured logs / state traces, forbidding silent error swallowing (see docs/07 §2.5); cross-module events should carry `trace_id` so the link on the event bus can be reconstructed by AI during debugging (echoes docs/07 §3 black-box diagnosis).

### Decision Convergence

Before producing architecture contracts (Interface / DTO / event structures), run an explicit "question → answer → persist" loop on decisions that affect the AI execution boundary — **never rely on the AI answering its own questions** (principle: skill-doc-principles §7):

- Question scope: module boundaries, cross-module communication style (sync/async), Facade exposure surface, event structure design, tech choices.
- Route tech-choice answers to `dm-adr`; never leave Q&A only in the chat stream.

## Workflow

### Step 1: Architecture & Interface Design (human-led, AI-assisted)

Clarify module boundaries, co-produce Interface and DTO with AI — output lands in `docs/06` contract SSOT. Run "Decision Convergence" here.

### Step 2: Generate Anti-Corruption Tests (AI-generated, human-reviewed)

Generate unit/integration test cases from the Interface to lock expected behavior (see docs/08 §2.2 Agentic TDD: core logic only, run in isolated process, Asserts constrained by docs/07). Delegate to dm-dev-tf.

### Step 3: Module Internal Implementation (AI-led, human Code Review)

Feed only the Interface + local context to AI, let it complete implementation inside the module until tests pass (execution granularity per docs/08 three-batch; if it descends into chaos, human runs `git reset --hard` to roll back, see docs/08 §2.1). Delegate to dm-dev-tf.

### Step 4: Global Integration (human-led)

Connect modules via Event Bus or API Gateway for end-to-end validation (validation output is docs/07 observability data).

> SOP aligns with `docs/01` §3.5 small-version execution steps: steps 1–2 ≈ Batch 1 (contract + data model), step 3 ≈ Batch 2 (Core single-file), step 4 ≈ Batch 3 (wire UI/call sites).

## Key Rules

| Rule | Source |
|------|--------|
| Unidirectional layering: Domain→Use Case→Adapter→Infrastructure, no reverse/cross-layer | This skill §Core Concepts |
| High cohesion low coupling: split by bounded context, not only by technical component | This skill §Core Concepts |
| Minimal exposure: each module exposes only via Facade/API, internals all private | This skill §Core Concepts |
| Contract-first: Interface/DTO/event before implementation; feed Interface to AI before implementing | docs/06 §2.8 |
| Module concealment: single index/facade entry, internal/services not public | This skill §Core Concepts |
| Cross-module decoupling: sync via Mediator/RPC, async via Event Bus, no hard-coded mutual refs | This skill §Core Concepts |
| Observability built-in: structured logs on key paths + no silent swallow + trace_id on cross-module events | docs/07 §2.5/§3 |
| Decision points explicit "question→answer→persist"; tech choices trigger dm-adr | skill-doc-principles §7 |
| Anti-corruption tests for core logic only; UI/views skip TDD | docs/08 §2.2 |
| Module implementation single-file/single-function granularity; chaos rolled back by human `reset --hard` | docs/08 §2.1 |

## Assets

- `docs/06-contract-based-dev.md` — contract-read-only SSOT
- `docs/07-observability-driven-dev.md` — observability built-in
- `docs/08-small-batch-iteration.md` — AI execution granularity & three-batch
- `docs/01-project-dev-flow.md` §3.5 — small-version execution step alignment
- dm-adr — tech-choice decision records
- `references/ai-collab-pillars.md` — index card for docs/06, 07, 08, 09 (pointers + key clauses only, load on demand when precise terms needed)

## Example

### Example 1: New module architecture

```
User: "design module boundaries and interfaces for the order domain"

AI:  1. Decision convergence (ask): module boundaries? sync/async comm? Facade exposure?
     2. Produce Interface + DTO (land in docs/06 contract SSOT)
     3. Give architecture guardrails (writable to .cursorrules)
     4. Delegate dm-dev-tf to generate anti-corruption tests + module impl (per docs/08 three-batch)
```

### Example 2: Generate AI guardrails

```
User: "generate AI guardrails for the project"

AI:  Output copy-pasteable guardrails for .cursorrules / CLAUDE.md:
     [AI Coding Guardrails]
     1. Do Not Cross Boundaries: access modules only via index/facade public exports
     2. Contract First: check Interface before implementing (see docs/06)
     3. Layering Rule: inner (Domain) must not depend on outer (Infrastructure/API)
     4. Minimal Surface Area: minimize public methods, default private/internal
     5. Event-Driven Coupling: cross-domain via Event Bus, no direct service calls
     6. Write Observability In: structured log on every non-trivial branch, no silent swallow (see docs/07)
     7. Stay In Scope: implement only the given single file / function; ask before expanding blast radius (see docs/08)
```
