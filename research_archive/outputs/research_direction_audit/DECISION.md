# Decision after the strict originality and feasibility audit

**Assessment: Share with caveats. Complete bounded originality and feasibility review; causal robustness remains partial.**

## Recommendation

Focus on whether the randomized program's effect on post-test total learning differs by continuous baseline teacher score. This is the strongest research question reviewed, using only the original released measurements and supplied normalization reference. It is a feasible exploratory seminar extension, not an established strong new finding.

The exact moderation question was not found in the original article, official eight-page appendix, erratum, or targeted searches of replication programs/logs. The paper already discusses qualifications generally, teacher-score attendance catch-up, learning by baseline writing, aggregate transition/dropout, and attendance-to-learning. The novelty is the specific added treatment-effect comparison, not those broader topics or originality across all literature.

## Verified evidence

- Learning reconstruction: all 16 Table9A/B coefficients, clustered SEs and N match at published precision. Small R-squared differences remain (maximum .005).
- Primary learning interaction: **.129 student-score SD per teacher-score SD**, SE **.071**, **95% CI [-.012, .270]**, exploratory **p=.073**, **1,646 pupils / 103 schools**. Positive but inconclusive.
- Independent regression algebra matches the coefficient/SE. Adding treatment interactions with the three original pupil-baseline controls gives **.126**, **95% CI [-.016, .269]**, same sample. One motivated check, not complete robustness.
- Government-school transition interaction: **+4.8 percentage points**, **95% CI [-10.5, +20.2]**, **p=.534**, **2,195 pupils / 111 schools**. The reconstructed Table10 anchor exactly matches all 2,197 archived child-level outcomes; two conflicting baseline IDs were excluded from the interaction.
- Secondary dropout-excluding-transfer interaction: **+16.3 points**, **95% CI [4.6, 27.9]**, **p=.0068**. Previously explored, not confirmatory. Outcome status uses last open-school checks, which the treatment affects; the small p-value does not resolve this measurement issue.

## Moderate and substantive scope

Use one main outcome (post-test total score), one baseline moderator (continuous teacher score), and one school-clustered interaction anchored in the original model. Consider complementarity, catch-up or no detectable difference as competing interpretations, not mechanisms identified by this regression.

Next assess missing-test and missing-teacher-score selection, and define a substantively meaningful heterogeneous effect. The current interval permits no difference and a substantial positive difference. Do not promise a significant result or claim that measured teacher skill itself causally converts attendance into learning.

Attendance catch-up is rejected as a main contribution because the original explicitly explains it. Generic weighting/robustness checks remain supporting work.

## Review coverage

Counts are scoped decision-aid units, not a universal verification percentage. Zero observed defects does not remove unresolved inferential limitations.

| Decision-aid quality | Observed defects | Assessment |
|---|---:|---|
| Usefulness/completeness | 0 / 4 directions | Two retained, two rejected with reasons. |
| Analytical clarity | 0 / 3 result groups | Learning, transition and secondary dropout show units, samples, CIs and caveats. |
| Visual/interaction consistency | 0 / 2 views | Explore/Compare, responsive evidence panel and navigation checked. |

| Analytical correctness and robustness | Observed defects | Assessment |
|---|---:|---|
| Source authority/confidence | 0 / 4 directions | Bounded original-material audit; wider literature not covered. |
| Value accuracy | 0 / 6 summaries | Anchors, contrasts and sensitivity reconcile with evidence; R2 discrepancy disclosed. |
| Within-chart agreement | N/A | No new quantitative chart. |
| Source details | 0 / 3 result groups | Scripts, CSVs, hashes where available and audit notes retained. |
| Cross-artifact consistency | 0 / 3 result groups | Site values mapped to current outputs. |
| Data-quality controls | 0 / 2 presentations | Missingness, conflicting IDs and observation-rule risks disclosed; selection unresolved. |
| Conclusion support | 0 / 4 decisions | Recommendation is for a question, not a guaranteed result. |

## Prioritized problems and remedies

1. **Originality overstated in the initial shortlist — fixed:** attendance catch-up and generic robustness no longer recommended as main studies.
2. **Exploratory findings mistaken for proof — fixed in presentation:** CIs, samples, prior exploration and limits appear beside results.
3. **Learning-selection uncertainty — unresolved:** descriptive attrition checks do not establish ignorable missingness. Next perform a bounded selection sensitivity.
4. **Transition measurement depends on opening — unresolved:** a credible dropout claim needs an explicit audit of that observation rule. Do not infer a harmful effect on writers from the interaction alone.
5. **Prior exploration — permanent limitation:** disclose it. A future plan cannot retroactively preregister inspected data.

## Reproduction

Run `python3 scripts/audit_learning_extension.py`, `python3 scripts/verify_learning_inference.py`, and `python3 scripts/audit_transition_extension.py` from the project root. Runtime recorded: Python 3.13.4, pandas 2.3.0, NumPy 1.26.4, SciPy 1.15.3. See `original_overlap_audit.md`, `learning_audit_report.md`, and `transition_audit.md` in this folder. Original raw files were not edited.
