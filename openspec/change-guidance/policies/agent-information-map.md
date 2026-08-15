# Agent Information Map Policy

> role: keep Deep Research contributor entry documents small, distinct, and routable
> trigger: adding material to `deep_research_harness/AGENTS.md`, `deep_research_harness/CLAUDE.md`, `deep_research_harness/README.md`, or `openspec/config.yaml`
> authority: guidance only; behavior, current facts, and path inventory remain with their owning contracts

## Reader Roles

Each entry document has one primary job. Link to the owner of detail instead of
copying it into another default reading surface.

| Surface | Primary reader | Job | Do not put here |
|---|---|---|---|
| `deep_research_harness/AGENTS.md` | Coding agent | Select the smallest relevant spec, source, test seam, and necessary interface | Product handbook, live-status report, exact path inventory, or command catalog |
| `deep_research_harness/CLAUDE.md` | Claude Code | Import the authoritative local coding guide | A second instruction set or product explanation |
| `deep_research_harness/README.md` | Human/operator | Introduce the product, provide quick start, and route deeper reading | Detailed architecture, operations, or testing reference |
| `deep_research_harness/docs/README.md` | Human/operator | Choose one focused human-facing reference | A second product overview or a full document dump |
| `deep_research_harness/docs/runtime-architecture.md` | Human/operator | Inspect downstream runtime and authority boundaries | Operations or test execution instructions |
| `deep_research_harness/docs/local-operations.md` | Operator | Run profiles, demos, diagnostics, and retained-session workflows | Runtime authority or coding-agent guidance |
| `deep_research_harness/docs/testing-and-evaluation.md` | Contributor/operator | Inspect test selection and evidence posture | The enumerable test registry or runtime behavior authority |
| `openspec/config.yaml` | OpenSpec author | State the product boundary, truth discipline, and change-authoring route | Full DeerFlow reference material, runtime facts, roadmap, or design history |

An ordinary coding change starts with the focus gate in `deep_research_harness/AGENTS.md`, not by
loading the README, every Change Guidance policy, or all of `openspec/config.yaml`. A policy
or deeper document is read only when its trigger or the change's Focus Card admits
it.

## Line Budgets

Line count is the primary deterministic attention budget. It measures the material a
reader must traverse before reaching a routing decision without pretending that words
or prose quality are mechanically comparable. The Change Guidance checker issues a warning
before it fails a hard budget.

| Surface | Warning | Hard failure |
|---|---:|---:|
| `deep_research_harness/AGENTS.md` | 120 lines | more than 160 lines |
| `deep_research_harness/CLAUDE.md` | 10 lines | more than 12 lines |
| `openspec/config.yaml` | 140 lines | more than 180 lines |
| `deep_research_harness/README.md` | more than 200 lines | none |

`deep_research_harness/README.md` must place `## Reading Map` within its first 80 lines and link to
`deep_research_harness/docs/README.md` plus the focused runtime-architecture, local-operations, and
testing-and-evaluation references. Its warning is intentionally advisory because
operator documentation may need durable detail; the map must make that detail skippable
for a reader who only needs one route.

The checker does not impose word-count quotas. Review decides whether a document is
clear, accurate, and appropriately linked; the line budget makes growth visible early.

## Placement Rules

When an entry document starts to explain a subject in depth, move the detail to its
existing owner and leave a brief pointer:

- exact repository paths and structural grammar stay in
  `openspec/governance/project-structure.toml`;
- required observable behavior stays in the owning OpenSpec capability spec/delta;
- current runtime facts stay in code, typed contracts, tests, and retained runtime
  authorities that own them;
- stable cross-capability principles stay in [`principles.md`](../principles.md);
- recurring review rules with a narrow trigger stay in a policy; and
- product orientation and quick start remain in the human-facing README; detailed
  architecture, operations, and test/evidence reference move to one scoped document
  behind `deep_research_harness/docs/README.md`.

The generated structure block in `deep_research_harness/AGENTS.md` is a locator, not a second path
inventory. It points to the registry, roots, grammar, and checker command. The TOML
registry remains the exact enumerated authority.

## Boundary

This policy does not make a line count a quality score, change what a capability
owns, or prohibit necessary documentation. It only preserves the entry documents as
maps so people and coding agents can decide what to read next without first absorbing
the whole project.
