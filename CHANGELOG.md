# Changelog

All notable changes to the P2 SMS audit codebase, paper, and
replication bundle. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

The version timeline mirrors the editorial-revision rounds, since
this repository is a single-paper artefact rather than a software
release stream.

---

## [Unreleased]

### Added
- Cloud Agent bootstrap: `.cursor/environment.json` plus
  `scripts/cloud-agent-install.sh` / `scripts/cloud-agent-start.sh`
  so new conversations can reuse a prebuilt Python environment.
- `archive/` directory: historical snapshots of v1-v8 manuscripts,
  cover letters, build scripts, process summaries, and v2 figures.
- `PROJECT_STRUCTURE.md`: file-by-file walkthrough of every top-level
  directory.
- `CONTRIBUTING.md`: external-contribution and review-feedback policy.
- `RELEASE_CHECKLIST.md`: pre-publication self-audit checklist.
- `.github/`: issue/PR templates + sanity-check CI workflow.

### Changed
- Top-level `README.md` rewritten as GitHub-ready front page (project
  layout, quickstart, citation, licence, maintainer).
- `submission/` cleaned: only `p2_ist_final.{tex,pdf,docx}` and
  `cover_letter_final.{md,pdf}` remain.
- `figures/v2/` moved to `archive/figures_v2/` (lineage retained).
- `docs/STATE.md` synced: path corrected, stage updated to round-9
  submission-ready.

### Removed
- Regenerable LaTeX byproducts (`*.aux`, `*.log`, `*.out`, `*.spl`)
  from both `submission/` and `archive/submission_drafts/`.

---

## [round-9] — 2026-05-03 (submission-ready)

### Added
- Final IST submission package: `submission/p2_ist_final.{tex,pdf,docx}`.
- Cover letter, round 8 (cover_letter_final).

### Changed
- Build script `build_ist_submission_v9.sh`: post-humanizer LaTeX
  generation; preserves the round-8 structural changes.

---

## [round-8.5] — 2026-05-02 (compliance and polish)

### Changed
- IST front-matter compliance: Highlights bullets ≤ 85 chars,
  Abstract ≤ 350 words structured.
- Humanizer em-dash sweep across §1-§9 + Appendix.
- Reference audit (paper-search MCP): all citations cross-verified
  via Crossref / DBLP / arXiv / Semantic Scholar; audit log in
  `docs/review_2026-05-02/reference_verification_audit.md`.

### Removed
- `v3b` and `v4-mp1` analysis residues (selection-on-the-response
  contamination); demoted to `R11` Appendix mention only.
- Abstract retroactive softening of unreachability claim.

---

## [round-8] — 2026-05-02

### Added
- Three-residual-threats statement in §7 (singular-matrix HP,
  per-class Kendall's W power, K_eq sweep stipulated alternative).
- §3.6 (ii) conceptual analysis of higher-order mutation
  reachability (defensive against prior-art HOM critique).
- Statistical-indistinguishability note in §3.4.

### Changed
- "Categorically unreachable" softened to "unreachable under default
  first-order syntactic configurations" (round-8 P0 edit).
- Abstract restructured: H2 not-met statement first, then primary
  finding, then robustness checks.
- Sun et al. SPE entry corrected: 2023 → 2024 (Wiley print issue).

---

## [round-7] — 2026-05-02 (prior-art defensive pass)

### Added
- §1.1 acknowledgement of prior semantic-mutation work.
- §1.3 (iv) framing of semantic mutation operators as a metric
  upgrade rather than a wholly new family.
- 8 new prior-art reference entries (Just FSE 2014, Andrews 2005,
  Petrović & Ivanković 2018, Papadakis 2019, Tip 2024 LLMorpheus,
  Ammann & Offutt 2008, Vargha & Delaney 2000, DeMillo 1978).

### Changed
- Paper title: now leads with "framework contribution" (round-6
  retitle) and "When Same-Prompt LLM Source Diversity Doesn't Help"
  (round-7).

---

## [round-5..6] — 2026-05-01 (editorial corrections)

### Changed
- Editorial corrections E1-E3 (round-5).
- Cross-references and notation consistency (round-6).

---

## [round-4] — 2026-05-01 (R1-R4 reviewer-response pass)

### Added
- Stipulated-alternative power simulation (`compute_rq2_power_stipulated.py`):
  power point estimate 0.491 / CI-lower 0.868.
- Per-class Friedman + Bonferroni × 4 + Kendall's W (`compute_rq3_friedman.py`).
- Appendix B.6 (manual mutmut verification).
- §6.4 cost cross-reference to Appendix E.2 (0.5 person-day).
- §1.3.2 CPH grounding + 4 classical-tradition citations.
- §1.6.2 toy-scope explicit framing.
- §9.5 Corollary 9.1 generic statement.
- §6.5.3 air-gap incompatibility declaration.
- §1.1 scope tightening.
- §8.6 ASME V&V 20-2009 reference.
- Data-and-code-availability section with Zenodo placeholder.

### Changed
- Highlights bullet 4: v4 effect-size value qualified as exploratory.
- §5.7 H5 reframed: not-met → substantive finding.
- §5.2 / §5.4 consolidated: effective-n + power.
- §3.4 v4-mp1 / v4-mp5 naming convention defined once and reused.
- §5.3 reframed list header to "three planned + one robustness".
- Abstract Results split into Primary / Robustness.
- §6.1 v4-mp5 cross-reference added.

### Removed
- §6.5.2 YAML threshold listing (replaced with quarterly batch audit
  reframe).
- §6.5.3 hard threshold (retitle "long-term aspiration").

---

## [round-3] — 2026-04-30 (Stage 4.5 final integrity)

### Added
- Bilingual revision-response process record.
- Round-3 final-integrity report: PASS for revisions.

### Changed
- Humanizer pass: em-dashes eliminated from threats / limitations.
- §5.3 "feeds" → "supports" (academic-tone fix).

---

## [round-2] — 2026-04-29 (review-response phase)

### Added
- v3 IST submission package post Stage-3 review.
- v4×MP5 robustness contrast (strips R11 chained confounder).
- Response-to-reviewer letter for simulated review.

### Changed
- §3.4 † symbol convention defined once and reused.
- §5.5 / §5.6 † applied to v3b/v4-derived numbers.
- §5.3 added v4×MP5 robustness row (δ = 0.314).
- §8.1 finding (iii) rewritten with axis-decomposition framing.
- Abstract: first-order qualifier; Method first; Results separated.

---

## [round-1] — 2026-04-29 (Stage 5b initial submission)

### Added
- IST submission bundle: elsarticle LaTeX, cover letter, author block.
- Stage-5 IST tailoring: 26k → 9.5k main + 6k appendix.

---

## [Stage A-D infrastructure] — 2026-04-25..28

### Added
- 12 PUTs × 5 MPs × 60 cells experimental design.
- Dual-LLM mutator pipeline (Claude Opus + GPT-5.4 + DeepSeek arbitrator).
- 3-layer LRCA classifier (L0 artefact / L1 tolerance / L2 OOD / L3 assumption).
- E1∧E2 equivalence judge.
- 116-test pytest suite covering PUT/MR/AVP/LRCA/equiv/stats/integration.
- Cosmic-ray syntactic-mutant comparison pipeline (1,250 mutants).
- v1 (single-source) and v3/v4 (cross-source) campaign infrastructure.

---

## Project conventions

- Each round corresponds to one revision-and-rebuild cycle. Rounds
  are *not* semantic versions; they are editorial milestones.
- The single source of truth for paper numbers is
  `data/results/paper_numbers_v4.json`, regenerated from
  `scripts/build_paper_numbers.py`.
- The Zenodo archive will pin a single commit hash (round-9 final).
  Earlier rounds are preserved in git history and `archive/`.
