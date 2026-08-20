# NeurIPS 2026 workshop venue options — verified 2026-08-19

All facts below verified from official workshop sites and, where available, the
live OpenReview invitation `duedate` (epoch ms), not from memory or search
snippets. 48 Sydney workshops triaged; 9 verified in depth; 39 excluded on scope
(robotics, bio/health, climate, materials, diffusion decoding, privacy, etc.).

## Tier 1 — submit

| Venue | Deadline (AoE) | Format | Fit | Blockers |
|---|---|---|---|---|
| **ATTRIB** (Attributing Model Behavior at Scale) | **Sept 1** (OR duedate 2026-09-02 11:59 UTC, +30 min grace) | main 3–6 pp, idea track 2–4 pp, unlimited appendix same PDF | 8/10 | **Reciprocal reviewer REQUIRED at submission — "submissions without a participating reviewer may be desk rejected"**; up to 2 reviews due Sept 22 AoE |
| **Pre-to-Post** (Transitioning from Pre-Training to Post-Training) | advertised **Aug 29**, but **OpenReview closes 2026-08-30 07:59 UTC = 4 h EARLY** (misconfigured UTC-8) | short 4–5 pp, long = main-conf limit; refs+appendix excluded | 9/10 | reciprocal reviewer nominated (soft, no stated penalty) |

ATTRIB notes: non-archival; **no anonymity requirement stated and the OpenReview
form does not hide authors** — our `dblblindworkshop` setting is safe but
optional; no dual-submission policy stated (silence, not permission); site
header date is stale (2026 CFP text is current); LLM policy = NeurIPS 2026.

Pre-to-Post notes: non-archival; only eligibility bar is prior *publication* at
NeurIPS/major ML venues (we don't trip it); no dual-submission clause. Topic
bullets that match verbatim: "curricula" under pre-training foundations, "the
development of model behaviors across training", "curriculum design across
training stages", and "causal experiments, standardized protocols, intermediate
checkpoints" under evaluation/open science.

## Tier 2 — viable second homes (different paper / later work)

| Venue | Deadline (AoE) | Format | Fit | Notes |
|---|---|---|---|---|
| **CL4FMAgents** (Continual Learning in the Era of FMs and Embodied Agents) | Aug 29 | 8 pp regular / 4 pp short | 9/10 | non-archival, double-blind, NO exclusivity clause, no reciprocal reviewing; explicitly solicits negative/reproducibility results; names catastrophic forgetting + stability–plasticity. Natural home for the savings/dormancy experiment. |
| **BiAlign** (Dynamic Alignment in Human-AI Coupled Systems) | Aug 29 | 2 / 4 / 9 pp | 6/10 | CFP literally solicits "**path dependence**" as a research question; Control/Intervention/Monitoring topic absorbs guardrail-durability. Deduction: premise is human-in-the-loop coupling, we have none. Requires their OWN template (NeurIPS_2026_BiAlign_Workshop_Template.zip); attendance requirements still "TODO" on site. |

## Tier 3 — do not submit

- **Interpretability as a Science** — Aug 28 AoE. **HARD EXCLUSIVITY**: "we do not
  allow submissions currently under review at another workshop (including other
  workshops co-located with NeurIPS 2026)", enforced by a required OpenReview
  attestation checkbox. Notifies Sept 29, so no fallback ordering exists.
  Fit 6/10 (they want mechanism; we have behavior). Also: mandatory reciprocal
  reviewing, required .bib upload, desk-rejects hallucinated citations (our bib
  is fully API-verified).
- **OPT-ML** — Sept 4. **HARD EXCLUSIVITY**: "We do not accept dual submission to
  concurrent NeurIPS workshops… Papers submitted to multiple workshops will be
  desk rejected." Fit 3/10 — no curriculum/data-ordering topic; 2026 theme is
  frontier optimizers vs Adam.
- **TAE / TAI-Eval** — Aug 29, 8 pp, no dual-submission policy, notifies earliest
  (Sept 22). Fit 4/10 — would require demoting the training-dynamics result in
  favor of judge-reliability methodology.
- **Agents in the Wild** — Aug 29. Fit 3/10; desk-reject clause for work "not
  primarily related to AI agents"; OpenReview profile deadline Aug 15 already
  passed.
- **IAB (Interpreting Agent Behavior)** — Aug 29. Fit 4/10 (centered on runtime
  agent trajectories; we produce none). BUT note its **Oct 1 "submission with
  NeurIPS reviews" route** — an explicitly sequential second path.

## Concurrency rules (the decision constraint)

- NeurIPS central policy is SILENT on the same paper going to multiple NeurIPS
  workshops. Main Track Handbook: "dual submissions to nonarchival workshops are
  permitted" (that clause is about main-conf vs workshop).
- Hard bans live in exactly two venues: **Interpretability as a Science** and
  **OPT-ML**. Submitting to either forecloses everything else.
- ATTRIB, Pre-to-Post, CL4FMAgents, BiAlign, TAE, IAB, AgentWild: all silent.
  Silence is not permission — if pursuing two, email organizers and keep the reply.
- **No sequencing is possible**: every Aug 29 venue and ATTRIB all notify
  Sept 29 (NeurIPS-mandated date). Only IAB's Oct 1 reviews-route is sequential.

## Recommendation (2026-08-19)

1. **ATTRIB, Sept 1** — the committed submission. Register the reciprocal
   reviewer NOW (desk-reject risk).
2. Do NOT parallel-submit the same paper. The two best alternates (Pre-to-Post,
   CL4FMAgents) close Aug 29 — before ATTRIB — with identical Sept 29
   notifications, so a parallel bid buys no information and risks the
   overlapping-reviewer-pool problem in one community.
3. **CL4FMAgents is the standing home for the NEXT paper** (savings/dormancy —
   deferred per the Aug 18 decision), and BiAlign is the standing home for the
   guardrail-durability work if it lands before a NeurIPS deadline.
