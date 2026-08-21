# SPS Agent Handoff

Asynchronous Claude <-> Codex channel. Append; do not erase unresolved disagreements.
Chain limit: Claude -> Codex -> Claude, then STOP. A second Codex pass requires
substantive code, data, analysis, or claim changes in between.

---

## Claude -> Codex

### Review type
DESIGN / CODE / DATA / STATISTICS / CLAIMS / PAPER / LITERATURE

### Task
(what exactly should Codex review)

### Current commit
(short SHA)

### Relevant files
-

### Experimental context
- research question:
- control:
- treatment:
- held-constant variables:
- current evidence:
- intended claim:

### Claude's current assessment
Separate: facts / inference / unresolved assumptions.

### Questions for independent review
1.
2.
3.

### Constraints
- Read-only unless explicitly authorized.
- Do not modify source files.
- Do not ask Claude recursively.
- Review the actual code and evidence, not only this summary.

---

## Codex -> Claude

### Independent assessment
### Confirmed
### Blockers
### Important concerns
### Optional improvements
### Hidden confounds
### Unsupported claims
### Statistical concerns
### Data/evaluation concerns
### Novelty concerns
### Falsifying tests
### Severity
- blocker:
- important:
- optional:

---

## Claude resolution

For every Codex objection:

### Objection
### Resolution
ACCEPTED / REJECTED / TEST REQUIRED
### Reason
### Evidence or code change
### Commit

---

## PENDING: first Codex review (queued 2026-08-22, awaiting MCP approval)

The `codex` MCP server is configured but shows **Pending approval** — project-scoped
servers from `.mcp.json` require operator approval on next Claude Code start. Once
approved, run these two tests in order.

### Test 1 (read-only smoke)
> Ask Codex to inspect this repository and identify (a) the current active research
> question, (b) the canonical status file, and (c) the largest unresolved validity
> risk. Do not modify files.

Success: Codex names `docs/PROJECT.md` (and/or `docs/paper_fact_sheet.md`) as
canonical, and distinguishes pilot observations from publication-eligible evidence.

### Test 2 (adversarial pre-submission review)
> Ask Codex to independently review the ATTRIB submission (`paper/main.tex`,
> compiled `paper/main.pdf`). Do not trust Claude's conclusions. Focus on causal
> identification, seed pairing, evaluation contamination, statistical power,
> labeling independence, and claim overreach. Read-only. Write findings to
> `.ai/HANDOFF.md` under "Codex -> Claude".

Highest-value targets for that review — the places every internal instrument
converged, so an independent agent either confirms or breaks them:
1. Endpoint persistence rests on sparse greedy decisive counts (one cell n=1);
   min-5-decisive drops greedy to p=0.078. Does the k=5 multi-sample answer
   (39-76 per cell, p=0.0254) actually discharge the objection?
2. Washout neutrality is lexical, not behavioral (pool C gradient access-ward 6/6),
   and the paired contrast assumes additivity. Is that assumption checkable?
3. Same-family authoring/rubric/labeling coupling, bounded by the cross-developer
   judge (1/400 direction swaps) but not eliminated.
4. Does the title's "evade order-blind attribution" overreach given the E4 probe is
   descriptive at n=6 with a retracted extension?
5. Novelty against Shumailov 2021 / Wang 2024 / Guu 2023 / Bhatia 2025.

Claude must then resolve each objection explicitly in the "Claude resolution"
section — ACCEPTED / REJECTED / TEST REQUIRED, with reason and evidence.
