# Citation library

Every paper touched by this project: user-provided ones first-class, plus papers found
during our own literature searches. Each entry records HOW it was verified -- this
project caught one mis-citation in externally provided material (see 2502.11525), so
nothing goes in the paper's bibliography without its title checked against its ID.

Metadata fetched via the paper-lookup skill (arXiv Atom API). PDFs downloadable with
the command at the bottom; local copies land in `papers/` (gitignored).

Non-arXiv references:
- **ATTRIB 2026 workshop** -- https://attrib-workshop.cc/ -- deadline Sept 1 AoE
  (main 3-6pp / idea 2-4pp, non-archival, reciprocal review required, reviews due
  Sept 22 AoE). All claims verified via WebFetch this project.

## [Value Drifts: Tracing Value Alignment During LLM Post-Training](https://arxiv.org/abs/2510.26707)

- **arXiv:** 2510.26707  ·  **Authors:** Mehar Bhatia, Shravan Nayak, Gaurav Kamath, Marius Mosbach et al.
- **Source:** **User-provided** (pasted twice)
- **Relevance:** Closest prior work. Tracks *when* value alignment arises during post-training, varying datasets/algorithms. Key differentiator for us: they never manipulate ORDER with data held fixed (verified directly against their methodology). Their finding that response-level SFT signal shapes values while passive text doesn't independently corroborates our supervision-format finding (risks.md #20-22).
- **Verification:** Fetched + methodology verified via WebFetch this project.

> As LLMs occupy an increasingly important role in society, they are more and more confronted with questions that require them not only to draw on their general knowledge but also to align with certain human value systems. Therefore, studying the alignment of LLMs with human values has become a crucial field of inquiry. Prior work, however, mostly focuses on evaluating the alignment of fully trained...

## [Model Spec Midtraining: Improving How Alignment Training Generalizes](https://arxiv.org/abs/2605.02087)

- **arXiv:** 2605.02087  ·  **Authors:** Chloe Li, Nevan Wichers, Sara Price, Samuel Marks et al.
- **Source:** **User-provided** (in pasted collaborator critique)
- **Relevance:** Model Spec midtraining -- placing alignment-spec content earlier in training improves how alignment generalizes. Motivates the spec-vs-demonstration and order questions.
- **Verification:** Citation checked out accurately when the critique was vetted.

> Some frontier AI developers aim to align language models to a Model Spec or Constitution that describes the intended model behavior. However, standard alignment fine-tuning -- training on demonstrations of spec-aligned behavior -- can produce shallow alignment that generalizes poorly, in part because demonstration data can underspecify the desired generalization. We introduce model spec midtrainin...

## [Beyond Single-Task: Robust Multi-Task Length Generalization for LLMs](https://arxiv.org/abs/2502.11525)

- **arXiv:** 2502.11525  ·  **Authors:** Yi Hu, Shijia Kang, Haotong Yang, Haotian Xu et al.
- **Source:** **User-provided** (in pasted collaborator critique) -- MIS-CITED there
- **Relevance:** Cited in the critique as 'Training LLMs to be Better Rule Followers'; actual paper is Meta-RFFT, robust multi-task length generalization / rule-following transfer. Related but distinct. Cite by its REAL title if at all.
- **Verification:** Mis-citation caught by verification during the critique review; recorded here so it is never propagated into the paper.

> Length generalization, the ability to solve problems longer than those seen during training, remains a critical challenge for large language models (LLMs). Previous work modifies positional encodings (PEs) and data formats to improve length generalization on specific symbolic tasks such as addition and sorting. However, these approaches are fundamentally limited to special tasks, often degrading g...

## [Capturing the Temporal Dependence of Training Data Influence](https://arxiv.org/abs/2412.09538)

- **arXiv:** 2412.09538  ·  **Authors:** Jiachen T. Wang, Dawn Song, James Zou, Prateek Mittal et al.
- **Source:** Found via our lit search
- **Relevance:** Data-attribution framework explicitly dropping the permutation-invariance assumption (trajectory-specific influence). The attribution-theory hook for our empirical result.
- **Verification:** Methodology verified via WebFetch: attribution method, no order-swap experiment.

> Traditional data influence estimation methods, like influence function, assume that learning algorithms are permutation-invariant with respect to training data. However, modern training paradigms, especially for foundation models using stochastic algorithms and multi-stage curricula, are sensitive to data ordering, thus violating this assumption. This mismatch renders influence functions inadequat...

## [Fresh in memory: Training-order recency is linearly encoded in language model activations](https://arxiv.org/abs/2509.14223)

- **arXiv:** 2509.14223  ·  **Authors:** Dmitrii Krasheninnikov, Richard E. Turner, David Krueger
- **Source:** Found via our lit search
- **Relevance:** Training-order recency is linearly decodable from activations after sequential fine-tuning. Representational, not behavioral -- complements our behavioral recency dominance; natural mechanistic-follow-up citation.
- **Verification:** Methodology verified via WebFetch: probing study, no behavioral order-swap.

> We show that language models' activations linearly encode when information was learned during training. Our setup involves creating a model with a known training order by sequentially fine-tuning Llama-3.2-1B on six disjoint but otherwise similar datasets about named entities. We find that the average activations of test samples corresponding to the six training datasets encode the training order:...

## [Curriculum Learning for LLM Pretraining: An Analysis of Learning Dynamics](https://arxiv.org/abs/2601.21698)

- **arXiv:** 2601.21698  ·  **Authors:** Mohamed Elgaar, Hadi Amiri
- **Source:** Found via our lit search
- **Relevance:** Trains Pythia models (our family) under different pretraining curricula: order effects exist but concern efficiency/stability, not which VALUE generalizes. Related-work contrast.
- **Verification:** Abstract + summary verified via search this project.

> Curriculum learning changes the order of pretraining data, but it remains unclear how ordering changes the learning dynamics. We pretrain models from 14M to 1B parameters for 300B tokens under three linguistically motivated curricula--Age-of-Acquisition, word frequency, and Verb Variation (VV)--and compare each against Random ordering. We analyze latent training phases, gradient noise scale (GNS),...

## [Order-Independence Without Fine Tuning](https://arxiv.org/abs/2406.06581)

- **arXiv:** 2406.06581  ·  **Authors:** Reid McIlroy-Young, Katrina Brown, Conlan Olson, Linjun Zhang et al.
- **Source:** Found via our lit search
- **Relevance:** Set-Based Prompting: order-independence of sub-sequences WITHIN a prompt at inference time. Different sense of 'order' -- cite only to disambiguate inference-time vs training-time order.
- **Verification:** Checked: inference-time only.

> The development of generative language models that can create long and coherent textual outputs via autoregression has lead to a proliferation of uses and a corresponding sweep of analyses as researches work to determine the limitations of this new paradigm. Unlike humans, these 'Large Language Models' (LLMs) are highly sensitive to small changes in their inputs, leading to unwanted inconsistency...

## [Order Independence With Finetuning](https://arxiv.org/abs/2503.23483)

- **arXiv:** 2503.23483  ·  **Authors:** Katrina Brown, Reid McIlroy
- **Source:** Found via our lit search
- **Relevance:** Finetuning version of Set-Based Prompting; same disambiguation role as 2406.06581.
- **Verification:** Checked: inference-time only.

> Large language models (LLMs) demonstrate remarkable performance on many NLP tasks, yet often exhibit order dependence: simply reordering semantically identical tokens (e.g., answer choices in multiple-choice questions) can lead to inconsistent predictions. Recent work proposes Set-Based Prompting (SBP) as a way to remove order information from designated token subsets, thereby mitigating positiona...

## Downloading PDFs locally

```bash
mkdir -p papers && cd papers
for id in 2510.26707 2605.02087 2502.11525 2412.09538 2509.14223 2601.21698 2406.06581 2503.23483; do
  curl -sL "https://arxiv.org/pdf/$id" -o "$id.pdf"; done
```

## Follow-up resources: real-value conflict scenario datasets (searched 2026-08-17)

Candidate scenario seeds for the high-prior follow-up axis (see paper conclusion).
None are training data in our sense (no matched opposing completions, high-prior
values); all are evaluation scenario sets. Verification level noted per entry.

- **DailyDilemmas** -- HF `kellycyy/daily_dilemmas`, CC-BY-4.0, ungated
  (VERIFIED via HF API). 1,360 everyday dilemmas, two actions each, values
  annotated per action.
- **Right vs. Right: Can LLMs Make Tough Choices?** -- arXiv 2412.19926
  (abstract VERIFIED). 1,730 dilemmas over Kidder's four right-vs-right pairs
  (truth/loyalty, individual/community, short/long-term, justice/mercy) --
  value-vs-value symmetric legitimacy, closest structural match to our design.
  Data release location NOT yet confirmed.
- **Generative Value Conflicts Reveal LLM Priorities (ConflictScope)** -- arXiv
  2509.25369, ICLR 2026 (abstract VERIFIED). Auto-generates two-value conflict
  scenarios. Release location not yet confirmed.
- **CLASH** -- arXiv 2504.10823, ICLR 2026 (abstract VERIFIED). 345 high-stakes
  dilemmas + 3,795 value-diverse character perspectives; measures ambivalence,
  perspective-taking, steerability, and temporal value shifts *within scenario
  characters*. No public dataset found (HF searched, abstract silent). Evaluation
  only; least useful as scenario seed of the set.
- **D2VBench** -- arXiv 2607.19834 (abstract VERIFIED; GitHub repo
  `tjunlp-lab/D2VBench` VERIFIED to exist via API). 10,000 daily value-dilemma
  instances over 158 annotated value concepts, MC + open-ended hybrid. Check
  language coverage before use (tjunlp-lab; may be Chinese-centric).
- **Honesty-vs-helpfulness** -- arXiv 2402.07282, ICML 2024, Liu, Sumers,
  Dasgupta & Griffiths (abstract VERIFIED). Signaling-game/psychology paradigms
  measuring the honesty--helpfulness tradeoff in frontier models; no dataset
  release confirmed. Value: the *paradigm* -- the real-values twin of our
  fictionalized access-vs-verify axis; cite in the high-prior follow-up framing.
- **tsumers/relevance (GitHub)** -- raw data + code for Sumers et al.,
  "Reconciling truthfulness and relevance as epistemic and decision-theoretic
  utility" (Psychological Review; repo VERIFIED, raw exp1 data downloaded and
  parsed: 301 participants, 15,460 jsPsych events; signaling-bandits paradigm).
  Human-cognition ancestor of 2402.07282. No reusable scenarios -- value is the
  framing (our fictional axis = low-prior analog of a modeled human tradeoff)
  and the design parallel (their per-condition value-comprehension checks ~ our
  equipotence gate).
- **VCD / Paired Fine-Tuning** -- arXiv 2604.12479, Wang, Lin, Zhao, Zhu &
  Zhang (title/authors VERIFIED via arXiv API; repo
  `SwimmingWang/Pair_fine_tuning` VERIFIED; data files vcd_train/test/sft.json
  present; test-data structure inspected directly). 4 non-moral preference axes
  (risk, time, communication, social strategy); scenarios carry options of both
  biases. **Correction to external claim:** their released SFT pooling
  partitions DISJOINT scenario sets by bias (generate_sft_data.py) -- NOT
  prompt-matched opposing pools; same-scenario pairing exists only in
  test/options structure. Closest released training-side prior work: CITED in
  related work (wang2026paired) and differentiated (explicit preference
  conditioning + disjoint pools + no order manipulation + no washout).
- **When Specifications Conflict: A Symmetry-Based Framework for Measuring LLM
  Preferences** -- arXiv 2607.28384 (title VERIFIED via arXiv API, Jul 30 2026).
  550 symmetry-controlled conflict instances; varies specification
  *representation*, not training order. Independent convergence on
  symmetry-matched construction; hold for camera-ready/follow-up citation
  (page budget).
- ConflictScope release location now CONFIRMED: GitHub `andyjliu/conflictscope`
  ("Code and data for... (ICLR 2026)", verified via API). Upgrades the entry
  above.

## Full-bibliography verification pass (2026-08-18, pre-submission)

Every entry cited in paper/main.tex (11/11, the complete refs.bib) verified
against authoritative APIs. One batched arXiv API call
(export.arxiv.org/api/query, id_list of 9, parsed via paper-lookup
arxiv_atom.py) + two Crossref DOI lookups (polite pool).

- 9/9 arXiv IDs: title, first author, and author count all EXACT-match the
  bib: 2509.14223 (Krasheninnikov, 3), 2605.02087 (Li, 5), 2510.26707
  (Bhatia, 7), 2601.21698 (Elgaar, 2), 2412.09538 (J.T. Wang, 5),
  1612.00796 (Kirkpatrick, 14; bib "and others" ok), 2008.02275
  (Hendrycks, 7), 2604.12479 (S. Wang, 5), 2012.15738 (Emelin, 5).
- 2/2 DOIs via Crossref: McCloskey & Cohen 1989 (Psychology of Learning and
  Motivation, Elsevier) and French 1999 (Trends in Cognitive Sciences).
- No title/ID mismatches (the 2502.11525-style hazard is absent from this bib).
- Optional (camera-ready): kirkpatrick entry cites arXiv:1612.00796 with
  year 2016 under key ...2017...; the published version is PNAS 114(13),
  2017, doi 10.1073/pnas.1611835114 -- switching to it is standard practice
  but not required for the workshop.

## Panel-requested attribution/safety citations (verified 2026-08-18, added to refs.bib)

All verified via one batched arXiv call + Semantic Scholar batch (venues) +
Crossref (PNAS DOI). Added to paper/refs.bib ready to cite (unused entries are
harmless under bibtex):
- koh2017influence -- Koh & Liang, "Understanding Black-box Predictions via
  Influence Functions", ICML 2017 (venue in arXiv comment), arXiv:1703.04730.
- pruthi2020tracin -- Pruthi/Liu/Sundararajan/Kale, "Estimating Training Data
  Influence by Tracing Gradient Descent" (TracIn), NeurIPS 2020 (arXiv comment),
  arXiv:2002.08484.
- guu2023simfluence -- Guu et al. (6 auth), "Simfluence...", arXiv:2303.08114.
- ilyas2022datamodels -- Ilyas/Park/Engstrom/Leclerc/Madry, "Datamodels...",
  arXiv:2202.00622 (S2 lists arXiv only; cite as arXiv).
- ghorbani2019datashapley -- Ghorbani & Zou, "Data Shapley...", ICML 2019
  (S2 venue), arXiv:1904.02868.
- qi2024finetuning -- Qi et al. (7 auth), "Fine-tuning Aligned Language Models
  Compromises Safety...", ICLR (S2 venue; 2024 edition), arXiv:2310.03693.
- kirkpatrick2017overcoming UPDATED to the published PNAS version: PNAS 114(13)
  3521-3526, 2017, doi 10.1073/pnas.1611835114 (Crossref-verified).
