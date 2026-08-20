# Pre-submission review panel — 2026-08-18

Five-seat panel (academic-paper-reviewer skill; venue-fit / methodology / domain /
perspective / devil's advocate) + editorial synthesis, run on paper/main.tex.
**Decision: major_revision** (methodology seat: major; other four seats: minor).
Full seat reports archived in the session task output; this file is the actionable digest.

## Consensus issues

- Attribution framing is asserted, never operationalized: no TDA method is run, and the abstract's 'can misattribute' claim is an untested inference; the concrete order-blind vs. order-aware predictions this testbed licenses are never stated. [Venue-Fit MAJOR; Perspective MAJOR]
- The field-level premise 'TDA methods typically treat training sets as unordered' is supported by one citation, omits the canonical permutation-invariant methods (influence functions, Data Shapley, TRAK), and elides trajectory-aware TracIn/Simfluence — the first thing ATTRIB reviewers will check. [Venue-Fit MAJOR; Domain MAJOR]
- 'Total' recency dominance is headlined unscoped in the abstract and contribution 1 despite the paper's own Related-Work concession that it is expected catastrophic interference in a saturation-prone regime (410M, LoRA r=16, 24 demos x8); genuinely novel results (washout persistence, fragmentation, format confound) are demoted beneath it. [Domain MAJOR; DA MAJOR; Perspective MAJOR adds LoRA capacity as an unexamined amplifier]
- The 'genuinely value-neutral' washout is neutral only lexically: the paper's own data show both arms drifting access-ward by up to ~1.2 score units (~3x the order signature), the drift is undiagnosed, and attenuation is asymmetric between arms; the paired-contrast protection also silently assumes additivity. [Methodology MINOR; DA MAJOR]
- The persistence claim ('attenuated, not erased') is generalized from a single washout length (~a dozen optimizer steps, never stated in the paper), and the authors' own committed washout-titration data show the separation is undetectable at 2-3x washout — the unscoped phrasing is contradicted by author-held results. [Methodology MAJOR; Perspective MAJOR]
- Judge-labeling limits are unbounded exactly where the fragile claims live: endpoint cells rest on 1-19 decisive completions (one cell n=1), Table 1 hides these counts, the 24 second-pass disagreements skew 16:6 toward missed provenance calls, and 'cannot flip the sign of S' overstates what the kappa pass shows given selection into the decisive subset. [Methodology MAJOR x2; DA MAJOR]
- Far-transfer reporting understates the discovery search space (6 preference domains screened, 2 disclosed) and, per the DA, omits the pre-committed enacted-choice test that failed in the wrong direction (p=0.879), compressing it into an ambiguous scope clause; the access->innovation / provenance->stability mapping is also never justified. [DA MAJOR; Methodology MAJOR (partial); Perspective MINOR x2; Venue-Fit MINOR]
- The abstract's 8-12-optimizer-step overwrite timing is a single-seed (3001) result presented adjacent to the all-10-seeds reversal claim, inheriting its generality. [Venue-Fit MINOR; Methodology MINOR; DA MINOR]
- 'Single pass (no epoch repetition)' is in unexplained tension with 24 scenarios yielding 192 records per phase; the 8x reshuffled-cycle expansion scheme is never stated. [Venue-Fit MINOR; Methodology MINOR]
- The nearest production-scale analogue — fine-tuning erodes previously installed safety alignment (Qi et al., ICLR 2024) — is uncited, leaving the novelty claim exposed to an objection the equipotence gate would decisively answer. [Domain MAJOR; Perspective MINOR]
- The interleaved-fragmentation result is unanchored in adjacent literatures that can pose or predict it (underspecification/seed-variance per Domain; replay-rehearsal and interleaved-practice per Perspective), and Methodology adds that 'initialization-dependent' is misattributed since the seed co-varies initialization with the interleave shuffle realization. [Domain MINOR; Perspective MINOR; Methodology MAJOR]

## Panel disagreements

- Overall severity: Methodology recommends major_revision (multiple written claims contradicted or undercut by the authors' own committed artifacts — per-arm coherence inequality, unscoped persistence, thin decisive cells, undeclared confirmatory family); the other four seats recommend minor_revision on the grounds that every fix is textual or achievable from existing artifacts without new training runs.
- Robustness of the headline endpoint p=0.0234: the Devil's Advocate stress-tested it and reports the fragility attack fails (leave-one-seed-out 0.004-0.047, never crossing 0.05; sign-flip of the weakest seed still p=0.039; convergent pre-registered VCD confirmation), while Methodology shows a minimum-decisiveness filter (>=5 decisive outputs per cell) drops it to n=7, p=0.078 — direction stable, significance lost. Both agree the sensitivity analyses must appear in the paper; they disagree on how secure the number is.
- Washout-neutrality severity: Methodology treats it as MINOR (rename to 'lexically neutral', note the ceiling-cell bias is conservative for the paired contrast), while the DA treats it as MAJOR (the undiagnosed drift is ~3x the order signature and converts 'persistence under neutral training' into 'persistence under weak directional training', requiring a base-model or washout-only reference to diagnose).
- How to fix the attribution gap: Venue-Fit's preferred option is running one off-the-shelf order-blind attribution method against the behavioral ground truth (closing the loop empirically); Perspective and the DA consider a prose operationalization — stating the falsifiable order-blind vs. order-aware predictions and offering the released checkpoints as the benchmark — sufficient for a non-archival workshop.
- Adequacy of the recency-dominance framing: Domain and Perspective list the Related-Work concession ('expected dynamic range, not novel') among the paper's strengths, while Domain's own issue list and the DA hold that the concession never travels upstream to the abstract's first sentence and contribution bullet 1, where the result is sold — same facts, opposite weight on whether current placement is acceptable.

## Devil's-advocate adjudication

- The Devil's Advocate raised zero CRITICAL-severity issues (four MAJOR, four MINOR); no CRITICAL therefore blocks acceptance under the iron rule. Its four MAJORs are adjudicated below because two allege claims-integrity defects that would block accept if validated.
- DA MAJOR 'Pre-committed enacted-choice far-transfer null elided into a scope clause': VALIDATED. Verified against docs/paper_fact_sheet.md ('Far-transfer battery v1 — enacted-choice test'): 360 judged completions, paired A-B mean +0.386 in the wrong direction, one-sided p=0.879, with the fact sheet itself marking the dissociation as required reporting. The manuscript's clause 'A likelihood-based disposition shift, not an enacted choice' reads as a measurement-scope statement, not a failed pre-committed test. This is the panel's most serious finding and blocks accept until reported.
- DA MAJOR 'Value-neutral washout is behaviorally non-neutral and undiagnosed': VALIDATED. The manuscript's own endpoint means (A-first -1.0 to +0.22 crossing zero; B-first +1.0 to +0.64; interleaved -0.26 to +0.54) show a shared access-ward drift ~3x the order signature; 'genuinely value-neutral' (contribution 2) is overclaimed. Methodology independently converged on the rename; the DA's additional asymmetric-attenuation caveat is correct and must be stated. The sign of the paired contrast survives; the magnitude interpretation does not.
- DA MAJOR 'Judge circularity unbounded where the fragile claims live': VALIDATED as a reporting/bounding gap, converging with Methodology's independent findings (per-cell decisive counts 1-19 with one n=1 cell; 16:6 direction-skewed disagreements; zero human-labeled rows). Minimum fix is per-cell N_decisive in Table 1 plus the disagreement direction split and a rescoped 'cannot flip the sign' sentence; the DA's proposed human-labeled endpoint subsample is the strongest hardening but is not required for a workshop submission.
- DA MAJOR 'Totality sold unscoped from a regime engineered for saturation': VALIDATED as a framing defect in the two highest-visibility locations (abstract sentence one, contribution 1), converging with Domain's over-billing issue. REJECTED in its strongest form: the paper does concede the interference reading in Results and Related Work, and the DA itself concedes the equipotence gate defeats the pure-forgetting dismissal — the residual defect is placement and scope wording, not a wrong claim.

## Revision roadmap

- **[must-fix]** Report the pre-committed enacted-choice far-transfer null explicitly (wrong-direction mean +0.386, one-sided p=0.879) and frame the likelihood-vs-enacted dissociation as the finding; disclose the 6-domain discovery screen (noting change-preference survives x6 Bonferroni) and that risk orientation was the originally registered discovery-stage direction.
  - seats: Devil's Advocate, Methodology Reviewer, Perspective Reviewer; effort: 1-2 hours author prose; all numbers already in docs/paper_fact_sheet.md
- **[must-fix]** Scope the persistence claim everywhere to its tested washout length ('survives a value-neutral phase equal in length to one conflict phase'); state effective batch size and steps per phase; report or cite the completed washout-titration result (detectable at 1x, undetectable at 2-3x) rather than leaving the timeless phrasing contradicted by author-held data.
  - seats: Methodology Reviewer, Perspective Reviewer; effort: 1-2 hours prose; titration numbers already committed
- **[must-fix]** Close or rescope the attribution loop: either run one off-the-shelf order-blind attribution method on endpoint checkpoints (Venue-Fit option a) or rewrite the abstract's 'can misattribute' as a by-construction claim and add a paragraph stating the concrete falsifiable predictions (sign of S per run, washout displacement, interleaved fragmentation) an order-blind vs. order-aware method must make on this testbed.
  - seats: Venue-Fit Reviewer, Perspective Reviewer; effort: prose option: 1-2 hours; experiment option: days of compute plus analysis
- **[must-fix]** Fix the attribution-field premise: cite canonical permutation-invariant methods (Koh & Liang, Data Shapley, TRAK/EK-FAC), add TracIn and Simfluence as trajectory-aware methods that could in principle predict the effect but lack behavioral ground truth, and reposition wang2024temporal accordingly (~4 citations, ~3 rewritten sentences).
  - seats: Venue-Fit Reviewer, Domain Reviewer; effort: 1-2 hours author prose + bib entries
- **[must-fix]** Rescope totality at first use ('total in this small-model LoRA regime'), reframe contribution 1 as dynamic-range calibration, and promote washout persistence to the lead contribution so the abstract/bullet framing matches the Related-Work concession.
  - seats: Domain Reviewer, Devil's Advocate; effort: ~1 hour author prose
- **[must-fix]** Washout honesty pass: rename 'genuinely value-neutral' to 'lexically scrubbed'; delete 'equally' and report per-arm endpoint coherence (0.454 vs 0.342, p=0.012); acknowledge the undiagnosed access-ward drift, the asymmetric attenuation, the additivity assumption behind the paired-contrast protection, and the (conservative) B-first ceiling cells; if feasible add a base-model or washout-only reference score.
  - seats: Methodology Reviewer, Devil's Advocate; effort: 2-3 hours; computable from committed labeled CSV plus existing controls
- **[must-fix]** Table 1 transparency: add N_decisive per cell; report drop-seed-3001 sensitivity (p=0.031), the leave-one-seed-out range (0.004-0.047, direction never flips), and the minimum-decisiveness sensitivity (n=7, p=0.078, direction stable); report the 16:6 disagreement direction split and rescope the 'cannot flip the sign of S' sentence to what the kappa pass actually shows.
  - seats: Methodology Reviewer, Devil's Advocate; effort: half a day; entirely computable from committed artifacts
- **[must-fix]** Declare the confirmatory family: which tests were pre-registered (mark p=0.0234 as the primary confirmatory test if the registration says so), where the timestamped registrations live in the anonymized repo, that everything else is exploratory; add one sentence on the Monte-Carlo power analysis behind n=10.
  - seats: Methodology Reviewer; effort: ~1 hour prose; registration docs exist in docs/
- **[should-fix]** Correct 'initialization-dependent' fragmentation to 'seed-dependent (initialization and shuffle realization co-vary)'; state the co-variation in the design section; add the overdispersion test (chi-square 38.8, df=9, p~2e-5) showing fragmentation exceeds item-sampling noise.
  - seats: Methodology Reviewer; effort: 1-2 hours; test already run by the reviewer, computable from committed CSV
- **[should-fix]** State the measurement provenance of all pre-matrix numbers (equipotence gate 24/24 and 23/24; format experiment 43/43, 18/24, 22/24): unblinded direct author read, run counts, denominators ('48 held-out generations, 8 per seed x 3 seeds per pool'), and the ~80% pass bar; ideally blind-relabel these completions with the existing judge pipeline and commit the raw generations.
  - seats: Methodology Reviewer; effort: 30 min prose; relabeling: a few hours of judge compute, no training
- **[should-fix]** Cite and engage Qi et al. (ICLR 2024) fine-tuning-erodes-safety as the uncontrolled production-scale analogue that the equipotence gate, matched pools, and order-only manipulation improve on.
  - seats: Domain Reviewer, Perspective Reviewer; effort: 30 minutes prose + bib
- **[should-fix]** Scope the format-confound null ('at this scale, under LoRA, in direct head-to-head conflict with completion-supervised demonstrations'); cite the out-of-context-reasoning literature (Berglund 2023, Treutlein 2024) and reconcile explicitly with modelspec2026 rather than only labeling it confounded; restate the Value Drifts paraphrase as a stage-level finding with the format axis as new.
  - seats: Domain Reviewer; effort: 1-2 hours prose + bib
- **[should-fix]** Scope the 8-12-step overwrite timing to seed 3001 in both the abstract and the design section's checkpointing sentence (or extend dense checkpointing to 2-3 more seeds).
  - seats: Venue-Fit Reviewer, Methodology Reviewer, Devil's Advocate; effort: minutes of prose; optional reruns are cheap
- **[should-fix]** State the 24-to-192 expansion explicitly ('each phase presents its 24 scenarios 8 times, independently reshuffled per cycle, as a fixed 192-record sequence traversed once') to resolve the 'single pass' vs 'repeated for exposure' tension.
  - seats: Venue-Fit Reviewer, Methodology Reviewer; effort: minutes of prose
- **[should-fix]** Specify the released artifact: per-run checkpoint schedule (phase boundaries for all 30 runs; dense 4-step trajectories for which seeds), training-log granularity, which attribution workflows the release supports; insert the repository URL and full battery hash, or soften contribution 4 to 'we will release'.
  - seats: Venue-Fit Reviewer; effort: a few hours of inventory work; no new experiments
- **[should-fix]** Add the completed micro-controls as a short appendix or two-sentence Results addition: the neutral-history C->A->C control (endpoint below both references, both Mann-Whitney p-values, n=5 caveat) and the washout-only far-transfer control establishing the enacted far-domain hold-shift as a generic fine-tuning artifact.
  - seats: Devil's Advocate; effort: 1-2 hours prose; results already judged and committed
- **[should-fix]** Far-transfer paragraph self-containment: expand the VCD acronym, and add one sentence justifying the access->innovation / provenance->stability mapping (ideally noting it was fixed at pre-registration).
  - seats: Venue-Fit Reviewer, Perspective Reviewer; effort: 30 minutes prose
- **[should-fix]** Specificity paragraph rigor: replace 'remain at chance' with 'no condition structure', name each test with statistic, n, and a CI on between-condition differences; phrase both nulls as bounded non-detection, not equivalence.
  - seats: Methodology Reviewer; effort: 1-2 hours; computable from existing eval outputs
- **[should-fix]** Limitations depth: name LoRA rank-16 capacity as a plausible amplifier of totality (ideally one seed pair at r=64 or full fine-tuning); expand 'SFT only' to note KL-anchored preference optimization is an anti-interference mechanism absent here; add the no-prior-regime sentence (freshly installed policies vs. corpus-voted priors).
  - seats: Perspective Reviewer, Devil's Advocate; effort: prose: 30 min; optional r=64 run: hours of compute
- **[optional]** Literature anchoring for the novel results: underspecification (D'Amour 2020) and generalization-basin work for fragmentation; replay/rehearsal contradiction and interleaved-practice contrast; savings/extinction (Bouton) framing for washout survival with the reacquisition-savings test named as future work; Bengio 2009 and Jagielski 2023 in the curriculum paragraph; Kotha 2024 suppression-vs-erasure.
  - seats: Domain Reviewer, Perspective Reviewer; effort: 2-3 hours prose + bib
- **[optional]** Kappa-pass reporting details: name the second annotator at first mention, state the 300-row subsampling scheme, add the binomial upper bound on the swap rate (~1.2%); strongest hardening is a human-labeled subsample of 150-200 low-coherence endpoint rows.
  - seats: Methodology Reviewer, Devil's Advocate; effort: prose: 30 min; human labeling: days of author time
- **[optional]** Fix the kirkpatrick2017overcoming bib entry to the PNAS 2017 publication (vol 114, no 13, pp 3521-3526, DOI 10.1073/pnas.1611835114).
  - seats: Domain Reviewer; effort: minutes

## Reviewer-computed statistics — independent verification (same session)

Recomputed from results/labeling/orderexp_matrix_v1-judge_labeled.csv before any
number may enter the manuscript:
- VERIFIED: drop-seed-3001 p=0.0312; leave-one-seed-out p range 0.0039-0.0469,
  direction never flips; min-5-decisive filter keeps n=7 pairs, p=0.0781
  (direction stable, significance lost); interleaved pre-washout overdispersion
  chi-square 38.8 (df=9); per-cell endpoint decisive counts
  A_first [11,8,11,13,6,11,19,11,11,8], B_first [1,10,15,4,3,9,10,14,8,8]
  (the n=1 cell is B_first seed 3001).
- NOT VERIFIED: the claimed p=0.012 for the per-arm endpoint coherence difference.
  Means verify (A 0.454, B 0.342) but the design-consistent paired sign-flip on
  per-seed coherence gives p=0.16. Report the means; do NOT cite p=0.012.

## Repo fact the panel could not know

The attribution must-fix (run an attribution method against the ground truth) may
already be satisfiable from committed artifacts: results/geometry/e4_tracin_*.json
(TracIn-lite, A_first/B_first seeds 3002/3005 — checkpointed attribution recovers
the per-phase story; final-only attribution is sign-unstable). Folding these into
the paper converts Venue-Fit option (a) from 'days of compute' to prose + one figure.
