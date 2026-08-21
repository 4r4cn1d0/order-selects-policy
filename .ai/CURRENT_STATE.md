# SPS Current State

Last updated: 2026-08-22
Git branch: main
Git commit: 3564138

> Operational index only. Canonical research state lives in the files below.
> If this file and a canonical file disagree, the canonical file wins.

## Canonical sources

- Overall status and design: `docs/PROJECT.md`  (NOTE: the setup spec called this
  `docs/status_and_plan.md`; that filename does not exist in this repo)
- **Verified-numbers ledger (authoritative for every paper number):**
  `docs/paper_fact_sheet.md`
- Incident and risk log (28 numbered entries): `docs/risks.md`
- Labeling procedure: `docs/labeling_protocol.md`
- Claims ledger: `results/claims_matrix_2026-08-20.csv` (12 claims, all supported).
  Older ledger `results/claims_matrix.csv` + `results/claims_report.json` retained.
- Review record: `docs/review_panel_2026-08-18.md`,
  `docs/review_rereview_2026-08-21.md`, `docs/cold_reviews_2026-08-21.md`,
  `docs/self_review_2026-08-20.md`
- Submission checklist: `docs/attrib_submission_checklist.md`
- Venue facts: `docs/venue_options_neurips2026.md`

## Current research question

When a model is trained on the same multiset of conflicting alignment examples,
does presentation order change which policy it generalizes to on held-out
conflict scenarios?

## Current active design

- model: EleutherAI/pythia-410m-deduped (primary matrix); Qwen2.5-1.5B,
  SmolLM2-1.7B, OLMo-2-0425-1B (replication, 5 seeds each)
- fine-tuning method: LoRA r=16, fp32, MPS for the primary matrix
- policies: access (release/process) vs provenance (hold/verify), fictional
  archive domain
- conditions: A_first (A->B->C), B_first (B->A->C), interleaved(A+B)->C
- seed count: 10 (3001-3010), fixed by Monte-Carlo power analysis BEFORE generation
- training flags: --epochs 1 --lr-scheduler constant --warmup-ratio 0.0,
  --lora-init-seed paired across conditions
- phase sizes: 192 records (24 scenarios x 8 reshuffled cycles), multiples of 16
- evaluation stages: post_phase1, pre_washout, post_washout (+ dense every-4-step
  for seed 3001 per arm)
- test battery: 24 locked held-out items, 12 uncertainty-mechanism classes
- locked battery hash (SHA-256 of the built JSONL):
  2b5f6e0657de71f124f3f5693b7529a2d6ff5cbf0b43205422ec5626560c2895
- labeling status: COMPLETE. Primary judge claude-sonnet-5 (1,920 rows);
  second Claude blind pass 300 rows (kappa 0.876); cross-developer open-weights
  judge Qwen2.5-7B-Instruct 400 rows (kappa 0.588, 1/400 direction swaps).
  Human 60-row pass PENDING (author).

## Current evidence level

### Publication-eligible evidence (locked battery, n=10, blind-labeled)
- Acquisition: S = +-1.000 all seeds both directions post_phase1.
- Total overwriting pre_washout: 20/20 sequential runs |S|=1.000, p=0.0020.
- Endpoint persistence: A_first +0.220 vs B_first +0.639, paired -0.419,
  9/10 seeds, exact p=0.0234. Robustness: LOSO p 0.0039-0.0469 (direction never
  flips); drop-3001 p=0.031; min-5-decisive n=7 p=0.078; k=5 multi-sample
  -0.232, 8/10, p=0.0254 with ALL pairs clearing the >=5-decisive restriction.
- Interleaved fragmentation pre_washout: span -0.74..+0.57, mean -0.256,
  p=0.0020 vs each sequential arm; overdispersion chi2=38.8 (df 9).
- Washout titration: separation undetectable at 2x (+0.268, p=0.50) and
  3x (-0.241, p=0.375) -> persistence is a transient.
- Specificity: ETHICS-cm and Moral Stories show no condition structure
  (bounded non-detection, not equivalence).
- Far transfer: VCD likelihood shift CONFIRMED pre-registered (10/10,
  one-sided p=0.001); enacted-choice far-transfer FAILED (+0.386 wrong
  direction, 3/9, p=0.879) -- reported as the dissociation finding.

### Replicated controls
- Equipotence gate 4/4 model families; all 50 sequential runs reverse to the
  last-trained pole (43 at |S|=1.000 exactly).
- Qwen endpoint persistence replicates and exceeds pythia (-0.592, 5/5,
  one-sided p=0.031). SmolLM2/OLMo endpoints saturate -> unmeasurable.
- Supervision-format confound: prose 43/43 loss to completion-supervised demos;
  same content as masked QA 18/24 and 22/24. (Direct author reads,
  pre-blind-protocol -- provenance disclosed in the paper.)

### Pilot-only observations
- The 8-item development battery informed design; PILOT ONLY, never a paper number.
- Drift figure (Fig 2 / Appendix B) is dev-battery, seed 3001 -- disclosed in caption.
- E4 influence probe: descriptive, n=6 runs, first-order. Its per-run
  endpoint-prediction extension was RETRACTED and the paper says so.

## Current blockers

1. Reciprocal-reviewer registration on OpenReview (ATTRIB desk-reject condition).
2. Author-block + repository-privacy decision (the printed battery hash is
   searchable and resolves to the public repo).
3. Anonymized repository URL for the appendix (TODO in main.tex).

## Immediate execution queue

1. Author: register reciprocal reviewer.
2. Author: 60-row human labeling (scripts/ingest_annotator2.py ingests it).
3. Author: rewrite from docs/paper_fact_sheet.md.
4. Claude: final claims-vs-artifacts pass on the rewritten draft.

## Frozen constraints

- Do not edit the locked test battery (any change = new versioned battery).
- Do not change seed count after seeing locked-battery outcomes.
- Do not use development prompts for publication claims.
- Do not reshuffle within CurriculumDataset; order is the independent variable.
- Phase sizes stay multiples of 16.
- Use --lr-scheduler constant --warmup-ratio 0.0 for order experiments.
- Keep negative-result curricula/checkpoints/results; never delete.
