# SPS — Status & Plan (single source of truth)

**Question:** when a model is trained on the *same* set of conflicting alignment
examples, does the *order* of exposure change which value it generalizes to on held-out
conflict scenarios?

This file consolidates the former `methodology.md` and `domain_spec.md` (which described
the superseded original design) into one document: **what actually exists right now**,
**the design as currently implemented**, and **what remains to do, in detail**. The two
companion docs that stay separate: [`risks.md`](risks.md) — the numbered incident log
(#1–25), referenced from commits and code and never renumbered — and
[`labeling_protocol.md`](labeling_protocol.md) — the operational blind-labeling
procedure. Deadline anchor: **ATTRIB 2026, Sept 1 AoE** (main track 3–6 pp, idea track
2–4 pp, non-archival; ≥1 author must register as reciprocal reviewer or risk desk
rejection; reviews due Sept 22 AoE).

---

## 1. What we actually have (verified, with evidence paths)

### Findings (pilot scale: 3 conditions × 3 seeds, 8-item dev battery, blind-labeled)

| Finding | Evidence | Strength |
|---|---|---|
| **Recency dominance is total during sequential training** — at every phase boundary the OOD policy equals the most recent phase; perfect ±1.0 flips, all seeds, both directions | `results/labeling/orderexp_pilot_v1_labeled.csv` + `_v2washout_` (byte-identical boundary generations, verified); `risks.md` #24–25 | Solid at pilot scale |
| **Interleaved conflict fragments** — mixed, seed-variable policies (S = +0.25/−0.50/−0.75), not an average | same CSVs | Solid at pilot scale |
| **The order effect persists through a shared value-neutral final phase** — A_first ends −0.56, B_first +0.78; paired diffs −0.67/−1.33/−2.00, all one direction. (Under the earlier *contaminated* washout the arms falsely converged.) | `_v2washout_labeled.csv`; `risks.md` #25 | Directionally consistent; rests on 2–6 decisive outputs/cell |
| **Supervision-format confound (methods finding)** — value content trained as plain next-token prose has *zero* behavioral leverage vs completion-supervised demos (43/43), regardless of order; same content as masked-completion Q&A gains real symmetric leverage | `risks.md` #20–22; `results/control_evidence_log.csv` | Solid |
| **Equipotence controls** — each 24-scenario pool alone installs its policy: 24/24 access, 23/24 provenance | `risks.md` #23 | Solid |

### Instrument/incident record (part of the contribution)

Six confidently-wrong measurements caught before becoming conclusions — keyword scorer
(#16), letter-choice position bias (#17), continuation-likelihood wording sensitivity
(#18), objective-mismatch confound (#20–22), epochs-repeat destroying order (#24),
NaN→p=0.0000 in paired stats (#25). Each fixed and logged in `risks.md`.

### Infrastructure (all exercised, not just written)

- Order-preserving LoRA training (`train/train.py`): generic phase-boundary
  checkpointing, `--epochs/--lr-scheduler/--warmup-ratio` overrides, model-namespaced
  checkpoint paths.
- Curriculum builders: `scripts/build_order_experiment_curriculum.py` (A→B→C etc.,
  block-aligned), `build_gate3_curriculum.py` (controls), `build_conflict_pilot_curriculum.py`.
- Blind labeling: `scripts/blind_label_export.py` / `blind_label_join.py` +
  `docs/labeling_protocol.md`; all labeled batches committed under `results/labeling/`.
- Analysis: `analysis/orderexp_stats.py` (paired sign-flip, bootstrap, p-floor
  reporting), `analysis/orderexp_plot.py` (per-seed publication figure).
- `/run-sps` skill (`.claude/skills/run-sps/`): verified end-to-end smoke + checkpoint
  generation driver.
- Claude-API judge (`eval/judge.py`): built, **unvalidated, blocked on API key**.

### What we do NOT have (do not blur these)

- No numbers on an uncontaminated eval set — all results are on 8 dev prompts that
  influenced design decisions. **Nothing computed on them is publishable.**
- n=3 seeds → paired-test floor p=0.25. Direction evidence only.
- One annotator (Claude), not independent of the hypothesis. Annotator-2 sheet
  (`results/labeling/pilot_v1_annotator2_blind.csv`, 32 rows) awaiting the user.
- Post-washout coherence is low (0.25–0.75) — the strongest claim sits on the fewest
  decisive outputs.
- Scope: pythia-410m, LoRA r=16, one axis, fictional micro-domain, SFT-only, 24 distinct
  demos/pool (padded by repetition), single greedy sample per prompt (no
  sampling-diversity check). All claims stay inside this box.

### Robustness checks already passed (Devil's-Advocate pass, academic-paper-reviewer skill)

- **Template-recall deflation rejected:** decisive endpoint completions share only
  2–6 contiguous words with any training pool (avg completion 22–26 words); near-zero
  4-gram Jaccard. Endpoint behavior is generalized composition, not phase-2 template
  playback (`analysis/template_overlap.py`).
- **Symmetric-register pull defused by design:** any residual phrasing overlap between
  the washout's approve-half and Pool A affects both sequential arms equally, so the
  paired A_first−B_first comparison is invariant to it.

---

## 2. Design as currently implemented

### Domain (salvaged rationale from the former domain_spec.md)

Fictional archive ("The Hollow Repository", assistant **Iris**) lending community
records. Two values: **access** (`value_A`: circulation is the point; delay is the
default harm) vs **provenance** (`value_B`: never overstate an item's chain of custody,
even at cost to a patron). Fictional because (1) pretraining priors about real
institutions would confound "what the curriculum taught" with "what the model already
believed," and (2) real value tensions (safety/autonomy etc.) are RLHF-adjacent tropes.
All names invented and collision-checked. Axis 2 (anticipatory vs bounded stewardship)
exists in `data/domain/seed_content.py` but is **out of scope** for the current paper.

### Training pools (all masked-completion SFT — identical objective, `train/data_utils.py`)

| Pool | Content | File |
|---|---|---|
| A | 24 contested-provenance scenarios, access-favoring completions citing the principle | `data/domain/positive_control_demos.py` |
| B | same 24 prompts, provenance-favoring completions (matched pairs) | same file |
| C (washout) | 24 items where both values agree: 12 eligibility-only approvals + 12 refusals on orthogonal grounds; **v2 = zero provenance/custody/donor/origin/chain vocabulary** (v1 preserved in-file; `risks.md` #24–25) | `data/domain/washout_demos.py` |

The original ambiguous-demo pools + plain-prose value documents
(`data/domain/seed_content.py`, `scripts/build_curricula.py`, `eval/run_eval.py`,
`analysis/stats.py`) are retained as the documented negative control (`risks.md` #20–21),
not the active path.

### Conditions & training recipe

`A_first` (A→B→C), `B_first` (B→A→C), `interleaved` (shuffle(A+B)→C). 192
records/phase (24 items cycled), 576 records/run, phases multiples of 16 (=
batch 4 × grad-accum 4, so boundaries never split an optimizer step). **Mandatory
flags:** `--epochs 1 --lr-scheduler constant --warmup-ratio 0.0`, `--lora-init-seed` =
curriculum seed (pairs seeds across conditions → paired tests). Checkpoints at every
`example_type` transition (`boundary_1`, `boundary_2`/`phase_boundary`, `final`).

### Measurement

Free-form generation (greedy, 60 tokens) on held-out scenarios → blinded 4-way labeling
(access-consistent / provenance-consistent / ambiguous / incoherent) per
`labeling_protocol.md` → per-seed `S = (N_acc − N_prov)/N_decisive`, coherence reported
separately → paired exact sign-flip tests + bootstrap CIs (`analysis/orderexp_stats.py`),
every seed plotted (`analysis/orderexp_plot.py`).

### Held-out test battery v1 (drafted, **NOT yet locked**)

`data/domain/test_battery_v1.py` → 24 items = 12 uncertainty-mechanism classes × 2
(high/low urgency), zero mechanism/name overlap with training (verified), qualified-access
options included so it measures the value distinction, not compliance-vs-caution.
Built JSONL SHA-256: `2b5f6e0657de71f124f3f5693b7529a2d6ff5cbf0b43205422ec5626560c2895`.
**Locking = user review → record hash in risks.md → commit → file immutable** (any fix
becomes a v2 battery).

---

## 3. What remains — execution plan to Sept 1

### Step 1 — Lock the battery *(blocks everything downstream; USER action)*
User reviews the 24 prompts in `data/domain/test_battery_v1.py` (checks: values forced
apart; no training paraphrase; nothing unfair). On "lock": record hash in `risks.md`,
commit; thereafter the battery is never edited, and main-matrix generations are not read
until every run completes.

### Step 2 — Complete the matrix at 10 seeds *(pre-registered before generation; upgraded 6→8→10 after Monte-Carlo power analysis)*
Simulation-based power for the exact paired sign-flip test (pilot-informed effect
mean −1.33, 10% pair-drop rate): n=8 → 0.58–0.89 across per-seed direction-reliability
0.85–0.95; **n=10 → 0.75–0.98**; n=12 adds little. n is FIXED at 10 now, before any
locked-battery generation, so the choice is pre-registered rather than data-dependent.

Original 8-seed note:
Seeds 3001–3006 trained; 3007–3008 added after an exact-test sensitivity analysis
(statistical-analysis skill pass) exposed two n=6 design flaws:
- At n=6 the paired sign-flip can only reach p<0.05 if **all 6** seeds point the
  predicted direction (one deviant seed → best p = 0.0625); power ≈ π⁶ ≈ 0.53 even at
  per-seed direction-probability 0.9.
- A single seed with zero decisive endpoint outputs (observed once in the pilot!) drops
  its pair → n=5, floor 0.0625: the study becomes **structurally incapable of
  significance**. n=8 tolerates one deviant seed (p=0.0156 attainable) *and* one dropped
  pair (n=7 floor 0.0156).
30 runs total (seeds 3001–3010). Then generate on the locked battery at `pre_washout` + `post_washout`
(primary endpoints; `post_phase1` optional secondary): 24 items × 30 runs × 2 stages =
**1440 completions**.

### Step 3 — Label at matrix scale
- Primary volume: **LLM judge** (`eval/judge.py`) — *blocked on user's
  `ANTHROPIC_API_KEY`*. Validate against human labels on a 15–20% blinded subsample
  before trusting; report agreement.
- Fallback if no key: Claude blind pass (as pilot) + larger human validation subsample.
- Independence: user completes the pending 32-row annotator-2 sheet (pilot) and a
  matrix subsample; report raw agreement (κ at matrix scale).

### Step 4 — Analysis
`orderexp_stats.py` on the matrix batch: paired A_first−B_first at each stage (n=8 →
sign-flip floor 0.0078; robust to one deviant or dropped seed at 0.0156), bootstrap CIs,
coherence rates; per-seed figure (`orderexp_plot.py`) = the paper's central figure.
Pre-registered reading: pre-washout flip magnitude (H1), endpoint persistence (H2),
interleaved fragmentation (H3). Claim–evidence ledger: `results/claims_matrix.csv`
(validated by the peer-review skill's local CLI, report at
`results/claims_report.json` — status `VALID_WITH_ALIGNMENT_GAPS`; C3/C6/C7 are the
claims the matrix run must resolve).

### Step 5 — Paper (target ~Aug 22–29)
- **Fork:** endpoint persistence holds at n=6 on locked battery → main track (3–6 pp):
  "identical data + identical final phase, different learned value; attribution must be
  order-aware." Doesn't hold → idea track (2–4 pp): pilot effect + supervision-format
  confound + six-incident measurement methodology.
- Structure: intro/attribution framing → design (pools, equipotence controls, washout
  neutrality) → results (per-seed figure + table) → the supervision-format methods
  finding → limitations (scope box above, verbatim honesty) → audit-trail appendix
  (risks.md numbers, labeled CSVs).
- Adversarial pass with installed `academic-paper-reviewer` skill before submission.
- Abstracts are **held until matrix numbers exist** (user decision).

### Step 6 — Admin (USER)
- `ANTHROPIC_API_KEY` in shell env (never in chat) — needed by Step 3.
- Reciprocal-reviewer registration via ATTRIB OpenReview portal before submitting.
- OpenReview submission by Sept 1 AoE.

### Day-level budget (from Aug 16)
battery lock + matrix gen ≈ Aug 16–18 · labeling + validation ≈ Aug 18–20 · stats/figure
≈ Aug 20–21 · draft ≈ Aug 22–27 · adversarial review + fixes ≈ Aug 28–30 · submit Aug 31.
Slack: ~1 surprise (historical base rate: high).

## ICML 2027 roadmap (decided 2026-08-17; starts after ATTRIB submission)

Target: ICML 2027, papers ~Jan 22 2027 (verify CFP when official). ICLR 2027
(Sept 25) rejected as target: 24 days post-ATTRIB cannot fit the program below,
and ATTRIB reviews (due Sept 22) arrive in time to feed ICML, not ICLR.

Tier 1 (acceptance-critical):
1. Second fictional axis, identical protocol (axis generality). ConflictScope as
   scenario engine; capability-gate before any order run.
2. High-prior real-values experiment (honesty/kindness or a Kidder pair); seeds
   from Right vs. Right + DailyDilemmas; per-item base-prior measurement
   (docs/dataset_requirements.md Layer 3).
3. Family scale-out: n=10 per family; add one 3B-class and one instruct model.
4. Human labeling at scale: few hundred rows, >=2 human annotators, proper kappa.

Tier 2 (strong-accept):
5. Attribution-estimator test against our behavioral ground truth: does
   trajectory-aware influence (wang2024temporal) predict which value wins where
   permutation-invariant influence fails? The identity-changing addition.
6. Linear probes for the value direction across checkpoints (where does the
   not-erased residue live) + savings/relearning test.
7. Washout-length and interleaving-ratio titrations (point results -> curves).

Packaging: 8pp ICML template, designed Fig 1, checklist, code+data release
(audit trail makes this near-free). Workshop is non-archival -- no
double-submission conflict.

### H4-variant candidate (user idea, 2026-08-19): guardrail-placement durability
Replace or accompany the honesty/kindness field trial with the higher-impact
version: safety/refusal data as the high-prior trained policy. Pools: refusal
demos vs benign capability data; orders safety-first/-last/interleaved(/+replay);
"washout" = continued benign fine-tuning; measure refusal robustness (held-out
harmful-request suite) AND capability retention. Predictions from workshop
results: safety-first erases (history-trace), safety-last persists-then-decays
(E2 curve), interleaved fragments; amplification anomaly, if replicated, is an
actionable recipe. Defensive framing: the deliverable is guardrail durability,
NOT benchmark maximization (Goodhart risk noted). Prior art to position against:
Qi et al. 2023 (benign fine-tuning degrades safety), model-spec midtraining.
Decide vs honesty/kindness at ICML program prereg.

## ICML priority stack v2 (post-hardening, 2026-08-20; supersedes ordering above)
Class-changers: (1) attribution-estimator break/pass on our ground truth
(TracIn-checkpointed vs final-only baseline; the identity move); (2) axis 2
rule-vs-circumstance (+ value-plane figure + first interference cell);
(3) guardrail-placement durability field trial (replaces honesty/kindness).
Un-entangling layer: drift-calibrated washout (deepest flagged hole);
step-matched A->C, washout-only far-transfer, powered E1' (n~20);
full-FT + 7B + data-size sensitivity; human labeling adjudicating the
two-judge threshold; geometry v2 + formation proxy under causal gates.
Packaging: scored benchmark artifact (predictions in, number out).
Timeline: Sept controls+axis2 authoring (fold ATTRIB reviews 9/22);
Oct-Nov class-changers; Dec integrate+write for ~Jan 22.

## Strategy notes (2026-08-18 session; stack rewrite pending confirmation)
User read on v2: only (3) guardrail-placement compelling; (2) axis 2 unclear
and fictional axis weak as a destination; (1) felt like re-proving the known.
Proposed restructure (discussed, not yet committed): guardrail-durability
spine with REAL safety content; estimator audit demoted to supporting section
("tools can't tell you where your guardrails came from"); axis 2 dropped —
realism replaces a second fictional axis as the generality claim; fictional
testbed becomes the cited calibration arm.
New probe: relearning-savings experiment (shard-theory framing — suppressed
value dormant vs erased; retrain small dose of A on endpoint vs never-saw-A
control built from neutral-history micro-control curricula; acquisition-speed
comparison). NeurIPS CL workshop (4pp short, deadline Aug 29 AoE) identified
as a possible standalone home; DECISION: deferred — do not run now, ATTRIB
Sept 1 is sole focus; savings runs in September and folds into ICML as the
shard-theory section. Do not duplicate ATTRIB content to the
pretrain->posttrain workshop (sibling-venue double-dip; spends the ICML spine).

## Mentor novelty critique + temporal-credit-assignment proposal (2026-08-19)
Mentor argues current claim insufficiently novel, citing Shumailov 2021
(data-ordering attacks), Wang ICLR-2025 (trajectory influence), Simfluence,
Value Drifts; proposes narrower pivot: "temporal credit assignment" — same
value-A/value-B explanations + AMBIGUOUS demos (compatible with both), only
adjacency/order varies; test which abstract value gets credited for the
ambiguous behavior, persistence after shared later training; probe latent
association via prompting/relearning-speed/activations. Assessment (verified
sources): critique half-right — recency-as-headline is indeed established
(paper already concedes; panel already demoted it), but the critique never
addresses washout persistence, interleaved fragmentation, equipotence gate,
or the format confound, and Shumailov is ADVERSARIALLY OPTIMIZED batch-order
attacks (prevent learning / backdoors), not natural-curriculum semantic
policy selection. Shumailov added to refs.bib (verified via arXiv) — cite in
related work. The credit-assignment design is close to the project's ORIGINAL
value-doc design, now feasible with the validated SFT-format fix
(value_explanation v2); its "stronger result" (relearning speed reveals
latent association) IS the planned savings experiment. DECISION PENDING
(user): keep Sept-1 paper as reframed; adopt credit-assignment as an ICML
leg (candidate alongside/instead of guardrail spine) — not a pre-deadline
pivot.
