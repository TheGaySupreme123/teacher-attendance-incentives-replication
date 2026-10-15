# Original-overlap audit: Duflo, Hanna, and Ryan (2012)

## Scope and source inventory

This is a bounded novelty audit of the official materials visible from the AEA article page and the complete local replication package. It does not estimate any new hypothesis models.

- Original article: `/Users/shayb/Downloads/Duflo-IncentivesWorkGetting-2012.pdf`; extracted copy: `tmp/pdfs/original_paper.txt`.
- Official AEA article page: <https://www.aeaweb.org/articles?id=10.1257/aer.102.4.1241>.
- The AEA page lists exactly three additional materials: Erratum, Replication Package, and Supplemental Appendix (saved HTML: `tmp/novelty_audit/aea_article.html`).
- Supplemental Appendix page: <https://www.aeaweb.org/articles/materials/1573>, redirecting to the official PDF at `https://assets.aeaweb.org/assets/production/articles-attachments/aer/data/june2012/20081207_app.pdf`. Retrieved copy and extraction: `tmp/novelty_audit/duflo_appendix.pdf` and `tmp/novelty_audit/duflo_appendix.txt` (8 pages).
- Erratum page: <https://www.aeaweb.org/articles/materials/14296>. Retrieved copy and extraction: `tmp/novelty_audit/duflo_erratum.pdf` and `tmp/novelty_audit/aea_erratum.txt` (1 page).
- AEA replication-package link: <https://doi.org/10.3886/E112523V1>. The public landing page returned HTTP 403 from this environment, so the local copy was audited directly: `data/Incentives_FINAL`, `data/Structural-Programs`, all `.do` files, Java source, shipped logs, and published-style CSV outputs.

The AEA page was fetched on 2026-09-22. The negative findings below mean “no corresponding table, figure, regression specification, or explanation was found in the article, the eight-page appendix, the erratum, or the local replication programs/logs searched.” They do not make claims about unpublished author work.

## What the original already does

The article already contains several pieces that constrain novelty:

1. **Teacher-score attendance heterogeneity and gap closing are explicit original results.** Table 2 reports above-median and below-median teacher-score effects of 0.15 and 0.24. The text says the larger low-score effect occurs because treatment brings low-score teachers to the same 78 percent attendance level as high-score teachers (article pp. 1248–50; `tmp/pdfs/original_paper.txt`, pages 9–11). `data/Incentives_FINAL/Programs/Table-2.do:86-140` implements the median split.
2. **Teacher score is already part of the structural attendance model.** The paper allows the outside option to vary with teacher test score and local control attendance (article pp. 1258–63; extracted pages 19–24). The online appendix contains only alternative structural-estimation details, fitted moments, and cost-minimization policies; it contains no student-outcome moderation analysis.
3. **Student learning already has baseline-writing, gender, and mid/post heterogeneity.** Table 7 Panel C reports child presence by whether the child took the oral or written pretest; Table 9 Panels C and D report learning effects for pretest-oral and pretest-written children; Panels E and F report girls and boys (article pp. 1269, 1272–73). A simple “learning differs by baseline writing” extension would therefore duplicate the paper.
4. **Transition and dropout are already headline outcomes, but only in aggregate.** Table 10 reports leaving the NFE, entering a government school, and dropout (article pp. 1273–74). `Table7_Table10.do:151-176` constructs `drop` and `gov`; `Table7_Table10.do:272-296` estimates only aggregate treatment effects.
5. **Attendance-to-learning is already analyzed.** Table 11 uses OLS and 2SLS to relate attendance to mid/post test scores and discusses measurement error, longer school days, and learning (article pp. 1274–75; `Table-11-Mid.do:238-257` and `Table-11-Post.do:271-303`). A generic “does attendance affect learning?” question is therefore not new.
6. **The paper already contains broad robustness and persistence checks.** These include the 80-school baseline-observation restriction (article p. 1247, footnote 10), period splits and post-test persistence (pp. 1248–50), the 25-visit attendance distribution (p. 1250), structural specifications with fixed effects, random coefficients, serial correlation, a three-day window, and block/teacher-score shifters (pp. 1258–66), and alternative appendix specifications (Appendix Tables 3–4).

## Candidate-by-candidate novelty audit

### 1. Treatment effect on student learning moderated by baseline teacher score

**Proposed question.** Does the randomized camera-plus-pay treatment change midline or post-test learning more in schools with lower or higher baseline teacher test scores? The estimand must be a treatment-by-baseline-teacher-score interaction in the Table 9 student-level outcome model, not a generic correlation between teacher score, attendance, and learning.

**Overlap found.** Teacher score appears as a control in original Table 9 Panel B, not as a treatment-effect moderator (article pp. 1272–73; `Table-9-Mid-Panel-BEF.do:222-243`; `Table-9-Post-Panel-BEF.do:263-284`). The article’s structural model uses teacher score to explain attendance, and Table 11 studies attendance and learning, but I found no treatment × teacher-score learning coefficient, plot, or explanation. The appendix is exclusively structural-model estimation and has no child learning tables or teacher-score learning interactions.

**Bounded conclusion.** The exact contribution appears absent from the official materials audited. A generic teacher-score/learning story would overlap; the narrow randomized moderation question remains potentially novel and substantively meaningful. Feasibility is moderate: all required raw tests and teacher scores exist, and the original Stata cleaning/normalization code is available, but the Table 9 sample construction, sentinel-value recoding, attrition/stayer rules, and school-clustered inference must first be reproduced exactly. This is the strongest candidate under the strict novelty rule.

### 2. Baseline-writing status × transition to government school or dropout

**Proposed question.** Does the treatment effect on government-school transition or dropout differ for children who could versus could not take the written baseline test? Use the original `gov` and `drop` definitions, then add a pre-treatment `treat × pre_writ` interaction. This is different from the original writing-status learning and attendance tables.

**Overlap found.** The original article reports baseline-writing heterogeneity for child presence and test-score outcomes, and separately reports aggregate transition/dropout outcomes. It does not cross baseline writing with transition or dropout in the paper’s tables or text. The local program confirms the separation: `Table7_Table10.do:227-265` uses `pre_writ` for attendance among non-dropouts, while `Table7_Table10.do:272-296` estimates aggregate `drop`, `gov`, and `drop2` without `pre_writ`.

**Bounded conclusion.** I found no exact baseline-writing-by-transition/dropout analysis in the article, appendix, erratum, or local replication programs/logs. The idea has moderate research value because it asks whether the program’s schooling transition effect is concentrated among children already closer to formal-school readiness. Feasibility is moderate: outcome construction is already coded, but the transition/dropout definition depends on the last five open random checks and must be merged carefully with the baseline writing roster. The paper’s explanation that written-test children gain more from learning means the motivation must be framed as a new transition margin, not as a new learning-by-writing result.

### 3. Continuous attendance-score gradient / formal gap-closing model

**Overlap found.** The exact continuous interaction is not in the original Stata programs or appendix, but the substantive claim is already in the article. Table 2’s median split and accompanying prose explicitly say that low-score teachers have a larger point estimate because treatment brings them up to the high-score attendance level (article pp. 1248–50). The structural model also already includes teacher score as an attendance shifter (pp. 1258–63).

**Bounded conclusion.** Under the user’s strict rule, this is not a sufficiently new primary contribution. The current continuous-gradient output formalizes and visualizes an explanation the original paper already gives. It can be a supporting descriptive or replication diagnostic, but it should not be presented as the paper’s new research question. The existing school-level gradient is additionally specification-sensitive because it uses a no-fixed-effect, equal-weighted school regression, while the repeated-check time-plus-block specification is weaker in the current artifacts.

### 4. Generic sensitivity or stability analysis

**Overlap found.** The original paper already reports multiple forms of stability: pre-treatment sample restriction, time-period persistence, long-run follow-up, distributional attendance comparisons, structural alternative specifications, a narrow month-boundary window, block and teacher-score controls, and appendix alternative models. The local `MasterDoFile.do` and program/log set reproduce these published analyses.

**Bounded conclusion.** “Check whether the result is stable” is too broad and overlaps the paper’s existing design. A targeted leave-one-school-out or alternative visit-weighting exercise does not appear in the audited files, but it would be a methodological robustness check with limited standalone research value. It is suitable as validation or an appendix, not as the substantive extension under the strict novelty requirement.

## Direction decision

Reject the current teacher-score attendance-gradient story as the sole new contribution: its exact regression is new, but its substantive interpretation is already the paper’s explicit explanation. Reject a generic learning, attendance-to-learning, baseline-writing learning, transition/dropout, or robustness story for the same overlap reasons.

The two bounded options that survive the audit are:

1. **Preferred:** treatment × baseline teacher score on standardized midline/post-test learning, after reproducing Table 9 exactly.
2. **Alternative:** treatment × baseline-writing status on government-school transition/dropout, after reproducing the original Table 10 outcome construction exactly.

Both are within the original experiment and use only existing raw data. Neither has been estimated in this audit.
