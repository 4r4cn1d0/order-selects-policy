# ATTRIB submission checklist — deadline Sept 1 2026, 23:59 AoE

Verified from https://attrib-workshop.cc/ and the OpenReview invitation on
2026-08-19. OpenReview `duedate` = 2026-09-02 11:59 UTC (= Sept 1 23:59 AoE),
`expdate` = 12:29 UTC (30-minute grace). Non-archival. LLM policy = NeurIPS 2026.

## USER — blocking items

- [ ] **Reciprocal reviewer registration.** The OpenReview submission form has a
      `reciprocal_reviewer` field; register via the Reviewer Registration Form
      linked in the OpenReview portal. CFP verbatim: "submissions without a
      participating reviewer may be desk rejected." Load: up to 2 papers,
      reviews due Sept 22 AoE. DO THIS FIRST — it also reveals whether the form
      is anonymous (see below).
- [ ] **OpenReview profiles for all authors** (profile creation/moderation can
      take up to 2 weeks for non-institutional emails).
- [ ] **Author block decision** (`paper/main.tex` line 33-38 still "Author TBD").
      ATTRIB states NO anonymity requirement and the OpenReview form does not
      hide authors. Two valid choices:
      (a) keep `\usepackage[dblblindworkshop]{neurips_2026}` and stay anonymous
          (safe, no action needed beyond removing the TBD block); or
      (b) switch to `[sglblindworkshop]` and insert the real author block.
- [ ] **Figure 1 regeneration** — caption still carries
      "[TO REPLACE: author-regenerated 10-seed locked-battery version]".
      Data: Table 1 / results/labeling/orderexp_matrix_v1-judge_labeled.csv.
- [ ] **60-row human labeling** (30 min) — see "Human labeling" below.
- [ ] **Anonymized repository URL** for the appendix (line 430 TODO), or drop
      the sentence.
- [ ] Final prose read of the rewritten draft.

## Human labeling (the last false-claim fix)

Sheet: `results/labeling/orderexp_matrix_v1-annotator2_blind.csv` (60 rows,
0 labeled). Condition/seed/stage already stripped; the key stays closed.

1. Open the offline labeling UI (no network, progress saves in-browser):
   `open <scratchpad>/label_60.html`  (regenerate any time; see below)
2. Label with keys 1-4 (access / provenance / ambiguous / incoherent).
3. "Copy CSV to clipboard", paste into a file, then:
   `python3 scripts/ingest_annotator2.py labels.csv`
   -> fills the sheet, joins to the judge labels, prints raw agreement,
   Cohen's kappa, cross-policy confusions, and a ready-to-edit paper sentence.

Payoff: Limitations currently must say agreement "bounds labeling consistency,
not human validity" (both annotators are Claude-family). With this done it
becomes a real human check, answering the review panel's judge-circularity
MAJOR. If human/judge agreement is BAD, that is a finding we need before
submission, not after.

## DONE (verified this session)

- [x] Every number in main.tex recomputed from committed artifacts
      (docs/paper_fact_sheet.md "Number certification pass").
- [x] Bibliography 100% API-verified (11 original + 7 added); Kirkpatrick
      upgraded to the published PNAS version (docs/citations.md).
- [x] Framing applied: title, abstract, contributions, vocabulary
      (docs/paper_fact_sheet.md "FRAMING DECISION").
- [x] Attribution premise properly cited (Koh & Liang, Data Shapley, Datamodels
      vs TracIn, Simfluence, Wang; Shumailov as adversarial complement).
- [x] Full battery SHA-256 in Appendix A; design section cross-refs it.
- [x] Compiles clean: 7 pages (main text within the 3-6 page main-track limit;
      appendix unlimited and in the same PDF, which ATTRIB permits).
- [x] E4 TracIn tallies verified from the 6 committed JSONs
      (docs/paper_fact_sheet.md "E4 TracIn-lite influence probe").
- [x] Five-seat review panel run; roadmap in docs/review_panel_2026-08-18.md.

## Rewrite must-fixes (from the review panel, all prose + committed numbers)

1. [DONE 2026-08-20 in the fallback main.tex; carry into the rewrite]
   Reported the pre-committed enacted-choice far-transfer NULL as its own
   result paragraph: 360 completions / 30 endpoints / 12 vocabulary-disjoint
   scenarios, paired diff +0.386 in the WRONG direction, 3/9 usable seeds
   negative, one-sided p=0.879, coherence 0.24-0.37, one seed dropped
   (zero decisive in one arm). Dissociation framed as the finding; 6-domain
   discovery screen and the x6 Bonferroni disclosed; risk orientation named
   as the first-registered direction (discovery p=0.060, confirmation
   p=0.24). Section heading changed to "...in likelihood space, but does not
   control enacted choice there." All numbers re-verified from
   results/labeling/far_transfer_v1-judge_labeled.csv on 2026-08-20.
2. Scope persistence to the tested washout length; cite the titration result.
3. Washout honesty: "lexically scrubbed" (done in tex), drop "equally", report
   per-arm coherence 0.454 vs 0.342 (means only - the panel's p=0.012 did NOT
   verify; paired test gives p=0.16).
4. Table 1: add per-cell N_decisive (one cell is n=1); add drop-3001 p=0.031,
   LOSO 0.0039-0.0469, min-5-decisive n=7 p=0.078.
5. Declare the confirmatory family and mark p=0.0234 as primary.
6. Optional but strong: fold in E4 TracIn (final-only identifies the last phase
   in 1/6 runs) as the attribution payload + the washout-drift diagnosis (pool C
   gradient is access-ward 6/6).

## STATUS 2026-08-22 (post-Codex) — 9 days to deadline

Machine-checkable work is COMPLETE. Final audit state:
- Claim ledger: 13 claims, 12 supported + 1 explicitly WITHDRAWN
  (cross-family judge invariance). No unresolved alignment gaps.
- Statistics audit: 19 verified / 1 partly-documented. The single remaining
  item is `reproducibility.data_materials_access` = the repository URL, which
  is an author decision, not an analysis gap.
- Body ends p6; refs p6; Appendix A (cross-family) p7; Appendix B
  (reproducibility) p8. Clean compile, no warnings.

### The four things only the author can do

1. **Reciprocal-reviewer registration on OpenReview.** Desk-reject condition.
   ~15 min. Do this first — it also reveals whether the form is anonymous,
   which settles item 3.
2. **60-row human labeling.** Now the single highest-value scientific item:
   after the E8 cut, there is NO non-Claude validation of the labeling task.
   Tool: open the labeling UI, then `python3 scripts/ingest_annotator2.py`.
   ~30 min.
3. **Author block + repository privacy.** ATTRIB states no anonymity
   requirement. If submitting non-anonymous, fill the author block and the
   hash-searchability issue disappears. If anonymous: repo private for the
   review window + scrub PDF timezone metadata.
4. **The rewrite**, from docs/paper_fact_sheet.md. Then Claude runs a final
   claims-vs-artifacts pass before upload.

### Deliberately NOT done (and why)
- E4 rerun beyond the gate: failed its precommitted criteria; rerunning until
  it passes would be exactly the practice this project exists to avoid.
- E8b corrected relabel: ~1 engineer-day for a claim the paper no longer needs.
- Fifth peer-review pass: would confirm, not discover (its tools check
  claim-evidence alignment, not instrument validity — the layer where all
  three Codex blockers lived).
