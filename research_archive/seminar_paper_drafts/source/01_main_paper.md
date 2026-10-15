# Attendance Incentives and Recorded School Departure by Baseline Writing Status

[Author name]

Reference draft prepared on October 7 2026

## Abstract

Does a teacher attendance program change recorded departure from nonformal schools differently for children with different initial preparation? I reanalyze Duflo, Hanna, and Ryan's randomized camera-monitoring and attendance-pay experiment in Rajasthan. The replication reproduces the headline attendance effect and the original average departure results. The extension adds one interaction between treatment assignment and baseline written-test status. Among 2,195 children in 111 schools, the program's recorded departure effect is 5.0 percentage points for baseline nonwriters and 26.1 points for baseline writers. The difference is 21.1 points, with a school-clustered 95 percent confidence interval of 6.9 to 35.3 points. The estimate remains positive under the specified sensitivity checks and within-family adjustment. It remains exploratory. Departure is an attendance-based classification whose observation opportunities depend on school opening; it does not establish withdrawal from education or a mechanism explaining departure.

## 1 Introduction

Does improving teacher attendance change recorded departure from the original school more for children who could already take a written test? This paper examines that question in the camera-monitoring and attendance-pay experiment studied by Duflo, Hanna, and Ryan (2012). The program increased teacher attendance, but its implications for a child's continued participation in the same nonformal education center may depend on the child's starting preparation. I reproduce the original attendance and average departure results, then add a single treatment interaction with baseline written-test status.

The main finding is a difference of 21.1 percentage points between the two groups' treatment effects on recorded departure. The estimated effect is 5.0 points among children who could not take the written baseline test and 26.1 points among children who took it. The direct test of that difference has a school-clustered two-sided p-value of .004 and a 95 percent confidence interval from 6.9 to 35.3 points. A school-level wild bootstrap gives p = .007. These estimates describe the original paper's attendance-based endpoint. They do not measure permanent withdrawal from schooling.

The distinction matters in this setting. Nonformal education centers provide basic instruction and can prepare children to move to government schools. Leaving the original center can therefore accompany educational progress. It can also reflect prolonged absence or disengagement. A rise in recorded departure cannot by itself distinguish these possibilities. The original study reports more government-school movement in treatment schools and no statistically resolved average difference in its residual dropout measure. The extension asks whether the aggregate departure pattern varies across a preparation margin measured before treatment.

Baseline writing status offers a substantive, feasible way to examine this variation. The original baseline protocol gave a written test to children who could write and an oral test to those who could not. This status identifies a difference in initial preparation, although it is not a comprehensive literacy measure. Children who already take a written test may be closer to moving beyond basic nonformal instruction. Children who do not may need more instruction at the original center. Those considerations motivate comparing treatment responses; they do not establish why an individual child leaves.

The contribution is a new comparison using an existing outcome and existing observations. The original article reports departure in aggregate in Table 10. It uses baseline writing status in its child attendance and learning analyses, but the audited article, supplemental appendix, erratum, and replication programs do not report a baseline-writing interaction for Table 10 departure. This is a bounded claim about those materials. The analysis does not claim priority over the wider literature, and it does not present the original average departure effect as a new finding.

The evidence requires two qualifications from the outset. First, the research direction was selected after examining several candidate extensions. The p-values remain exploratory, including the adjustment within the three departure-related outcomes. Second, the original endpoint uses the latest up to five observed checks at which a school was open. The program changes school opening, so it also changes the observations used to classify departure. I retain that endpoint for replication and assess its documented coding and coverage weaknesses. The paper's one point is that recorded departure under this rule responds differently across baseline-writing groups. Section 2 presents the replication. Section 3 explains the extension and its results. Section 4 discusses interpretation, and the appendix reports sensitivity and reproducibility details.

## 2 Original study and replication

### 2 1 The experiment and its main claim

Duflo, Hanna, and Ryan (2012) study single-teacher nonformal education centers run by Seva Mandir in rural Udaipur, Rajasthan. The centers teach basic Hindi and mathematics. A teacher's absence normally closes the center, so teacher presence and access to instruction are closely connected. The experiment initially randomized 120 schools, with 60 assigned to treatment and 60 to comparison. Seven schools closed after randomization but before the program was announced, leaving 57 treatment and 56 comparison schools in the evaluation.

The program began in September 2003. Teachers in treatment schools received cameras, and a student photographed the teacher and children at the start and end of the day. The date and time records supported an attendance-linked pay schedule. Comparison teachers continued to receive a fixed salary. Because monitoring and attendance pay were offered together, random assignment identifies the effect of the package. The design does not separately identify a camera effect or a pay effect.

The headline experimental claim is a reduction in teacher absence of about 21 percentage points. The authors also report a learning improvement of about 0.17 standard deviations and greater movement into government schools. Those outcomes concern different units and horizons. The headline attendance estimate uses school visits through February 2006, whereas learning is measured in child tests and departure is constructed from child roster histories. Keeping their samples separate is necessary for an honest replication.

### 2 2 Data reconstruction and replication procedure

I use the public version 1 replication package, distributed through openICPSR as E112523V1 (Duflo, Hanna, and Ryan 2019). The original programs are in Stata and contain older machine-specific paths. The replication here reconstructs selected results in Python from the original Stata data files and compares them with the paper and shipped output. It does not reproduce the structural labor-supply model or every published result. The focused replication covers the experimental headline and the outcomes needed for the extension.

For attendance, I apply the original school exclusions and time construction to the random-check file, omit the pre-announcement baseline period, and estimate a treatment-control difference in the indicator that the school is open. Each observation is a random school visit. The model includes an intercept and randomized treatment assignment. I allow observations within the same school to be correlated by clustering standard errors at school level. The resulting sample has 3,071 visits in 113 schools. The original time construction includes the late-August checks assigned to the September intervention period.

For departure, I reconstruct the enrolled child roster from the two raw roster sources, link the random checks and baseline records, and follow the Table 10 program's attendance recoding. The program sorts each child's open-school checks from newest to oldest and retains up to five. A child receives the departure indicator when attendance sums to zero in those retained rows. The same pipeline defines the government-school marker and the residual departure measure. Matching the published construction includes preserving the original string and numeric reason-field mismatch; Appendix B explains its implications.

### 2 3 What reproduces

[[TABLE replication]]

Table 1 shows that the reproduced headline attendance coefficient is 0.207, with a clustered standard error of 0.030. These round to the original 0.21 and 0.03. The treatment and control opening rates are 78.7 and 58.0 percent, respectively. The estimate corresponds to an increase of 20.7 percentage points in school opening, with a 95 percent interval from 14.9 to 26.6 points. This reproduces the headline experimental result without requiring the structural model.

The child departure reconstruction also matches Table 10 at its reported precision. In the 2,197-child replication sample, the treatment-control difference in total recorded departure is 8.4 percentage points, with a standard error of 4.1 points. The corresponding differences are 10.1 points for the recorded government-school marker and -1.8 points for the residual measure. These reproduce the published coefficients of 0.08, 0.10, and -0.02. The reconstructed child outcomes agree with the shipped reference records. Reproducing them verifies the implemented measure; it does not resolve the measure's interpretation.

The existing learning audit provides an additional check on the package: 16 selected Table 9 specifications match the shipped coefficients, standard errors, and sample sizes at reported precision. For example, the baseline-controlled post-test total coefficient is 0.173 with standard error 0.087 in 1,760 source records. I keep learning outside this paper's main extension. Appendix C records the alternative learning directions examined so that the choice of departure is visible.

## 3 Extension to baseline writing status

### 3 1 The question and analysis sample

The extension changes one part of Table 10: it adds baseline written-test status and its interaction with randomized treatment. The primary outcome remains total recorded departure from the original nonformal center. The question is whether the program changes this classification by a different amount for children with different baseline preparation. It does not ask whether being able to write causes departure. Writing status was measured before treatment, but it was not itself randomized.

I link the reconstructed child outcomes to baseline writing records using the school and child identifiers. Repeated baseline records must agree on written-test status. Two eligible child identifiers have conflicting status and are excluded rather than assigned a category. The resulting analysis has 2,195 children across 111 schools. It contains 1,798 baseline nonwriters and 397 baseline writers, with 1,136 treatment children and 1,059 control children. The 111-school departure sample differs from the 113-school attendance sample because the child roster construction supplies the departure observations.

I use the terms baseline writer and baseline nonwriter as concise labels for the test protocol. A baseline writer took the written baseline test; a baseline nonwriter did not. The labels do not measure a stable ability type or a complete set of educational skills. I keep this binary classification fixed. No score threshold is chosen to maximize the interaction, and no new observations or externally collected variables enter the analysis.

### 3 2 Outcome definition and estimand

The departure indicator equals one when the child's recorded attendance is zero over the latest available open-school checks selected by the original rule. It equals zero when the child has recorded attendance in that window. Some children have fewer than five selected checks, so the operational classification can rest on a shorter history. A zero therefore means the child was not classified as departed under the rule; it does not independently prove continuous enrollment. A one can also include a recorded government-school marker; it does not verify every child's destination.

I estimate a linear probability model for child i in school s:

[[EQUATION departure]]

Here Y is the binary departure classification, T is school treatment assignment, and W is baseline written-test status. The coefficient tau is the treatment-control difference for nonwriters. Tau plus delta is the corresponding difference for writers. Delta, the main estimand, is the writer treatment effect minus the nonwriter treatment effect. Because the model includes both binary main effects and their interaction, it reproduces the four observed cell means exactly. It weights children equally, rather than giving every school equal weight.

I calculate school-clustered standard errors with the finite-sample correction used in the audited Python implementation. The main confidence intervals and two-sided p-values use 110 cluster degrees of freedom, based on 111 schools. For the writer effect, uncertainty comes from the covariance of the treatment and interaction coefficients. Children in the two groups can attend the same schools, so the interaction's standard error is computed directly from the full model. It is not inferred by comparing the groups' separate significance labels.

The null-imposed wild-cluster bootstrap multiplies restricted-model residuals by a common random sign within each school and recomputes the interaction t-statistic. It uses 9,999 draws and seed 20260922, following the general cluster-bootstrap approach of Cameron, Gelbach, and Miller (2008). I also report Holm's (1979) adjustment across the three fixed departure-related interactions. These procedures address specified statistical uncertainty. Neither corrects an undocumented outcome definition or the full historical search across candidate research directions.

### 3 3 Observed group rates and the direct comparison

[[TABLE group_rates]]

Table 2 gives the four rates behind the interaction. Among baseline nonwriters, 290 of 858 control children and 365 of 940 treatment children are classified as departed. The rates are 33.8 and 38.8 percent, a difference of 5.0 percentage points. Among baseline writers, 89 of 201 control children and 138 of 196 treatment children are classified as departed. The rates are 44.3 and 70.4 percent, a difference of 26.1 points. These are comparisons between children in randomized schools, rather than changes within the same children before and after treatment.

[[FIGURE main_effects]]

Figure 1 shows both treatment effects and their directly estimated difference. The nonwriter effect has a 95 percent interval from -2.4 to 12.4 points. The writer effect has an interval from 10.0 to 42.3 points. Their difference is 21.1 points, with clustered standard error 7.2 points and interval from 6.9 to 35.3 points. The interaction's p-value is .004. The bootstrap p-value is .007, and the three-outcome Holm-adjusted p-value is .012.

The direct comparison supplies the evidence for heterogeneity. An individually significant writer estimate and an individually insignificant nonwriter estimate would not establish that the effects differ. Here the model tests that difference explicitly. Conversely, the interval for nonwriters does not prove that the program has no departure effect in that group. It admits both a small negative effect and a positive effect of more than ten points.

The 21.1-point estimate is the additional writer response, not the fraction of all children who leave because of the program. It also differs from the original aggregate departure estimate of 8.4 points. The aggregate pools children across writing groups and uses the two additional baseline-conflict records. The interaction answers a narrower question that the aggregate does not resolve. The smaller writer group makes its estimate less precise, but the magnitude and interval support a difference under the operational endpoint.

### 3 4 Departure and recorded destinations

[[TABLE outcome_family]]

Table 3 reports the three departure-related interactions together. The government-school-marker interaction is 4.8 points, with a 95 percent interval from -10.5 to 20.2 points and p = .534. The secondary residual departure interaction is 16.3 points, with interval from 4.6 to 27.9 points and p = .007. Its Holm-adjusted p-value is .014, and its wild-bootstrap p-value is .010. Showing the complete family prevents the total-departure result from standing beside selectively omitted destination evidence.

The decomposition requires care. Under the supplied code, total departure equals the government-school marker plus the residual outcome. The three point estimates obey that identity. Their statistical uncertainty does not supply a reliable account of educational destinations, however. Reasons are frequently blank, and the raw roster sources store them using different data types. A blank government-school marker is not evidence that a child stopped studying. The residual result therefore describes departure without the recorded marker, rather than proven educational dropout.

The current evidence also does not establish that the writer interaction operates through government-school transfer. The government-marker interval is wide and includes zero. The significant residual interaction does not establish a harmful effect either, because destinations outside the recorded marker remain uncertain. I treat these outcomes as a transparency requirement and an interpretive constraint, while keeping total recorded departure as the main endpoint.

### 3 5 Observation opportunities and the strength of the claim

The largest threat to a broader interpretation comes from the observation rule itself. The program increases school opening, which supplies more opportunities for roll call. Nonwriters average 15.4 open checks in control schools and 20.4 in treatment schools; writers average 15.2 and 21.9, respectively. Thus the latest five open checks need not cover the same calendar interval or the same opportunities for observing participation across groups. Random assignment supports comparison of the implemented classification, but it does not turn that classification into a treatment-independent measure of school exit.

Of the 2,195 children, 145 have fewer than five observed open checks. A separate audit flags 113 departure classifications that depend partly on undocumented attendance codes. The two sets overlap for 28 children, leaving 230 with at least one concern. These issues can change which absences the outcome counts and how much history it uses. They belong in the substantive interpretation, even when conventional statistical tests reject equality of the two operational treatment effects.

Appendix A reports the fixed block-control and calendar-endpoint checks, the exclusion sensitivity, and algebraic bounds that treat flagged outcomes as unknown. The point estimate remains positive in those checks. The point estimates and arithmetic lower bounds do not reverse under these specified checks. They do not establish that the outcome is independent of coding or treatment-dependent observation, recover unrecorded destinations, or make the exclusion sample representative. The appropriate claim remains heterogeneous recorded departure under the original roster rule.

### 3 6 What the exploratory search permits

The project examined teacher-score attendance differences, learning heterogeneity, learning-domain composition, and distributional learning outcomes before selecting this departure question. The final three-outcome family was fixed for the focused audit after those earlier inspections. Its Holm adjustment addresses multiplicity within that family. It does not account for every earlier outcome, specification, and direction considered, and it cannot make the present result an independently confirmed discovery.

The paper therefore reports a substantive exploratory pattern supported by clustered inference and source-based checks. It retains the unsuccessful learning alternatives in Appendix C rather than treating them as unseen. No further subgroup definitions, attendance windows, or outcome exclusions are introduced to obtain a smaller p-value. The descriptive contribution is still useful: the original aggregate departure result conceals a difference across an observed baseline preparation margin. The strength of that contribution depends on reporting how it was found and what the endpoint measures.

## 4 Discussion and conclusion

The replication reproduces the original experimental attendance result and the average departure outcomes. The extension finds that assignment to the bundled program changes the recorded departure classification more among children who took the written baseline test. The direct difference is 21.1 percentage points, with a school-clustered confidence interval excluding zero. This is the paper's main result. It refines the original average departure finding by crossing that outcome with a preparation measure already present in the data.

The result leaves the original teacher-attendance conclusion intact. More reliable teacher presence can coexist with a change in whether children remain observed at the original center. In a setting where nonformal schools can prepare children for government schools, departure is not a self-explanatory success or failure measure. The finding does not show that attendance incentives harm children's education, and it does not show that writing ability itself causes a different response. Both claims would require evidence that the present design does not supply.

The central limitation is treatment-dependent measurement. The last-open-check rule changes its observation basis when the program changes school opening. Coding ambiguity and incomplete histories compound that problem, while incomplete destination records limit interpretation of the residual outcome. The checks show that several documented coding concerns do not individually reverse the observed interaction. They do not resolve the broader measurement problem. Exploratory selection further limits what the statistical significance can establish.

The conclusion is consequently narrow and useful. Under the original paper's implemented roster measure, the program's departure response differs across baseline-writing groups. Reporting that distinction alongside the reproduced headline, the direct interaction, and the measurement limits gives a more complete account of the experiment than the aggregate departure coefficient alone. It supports a focused extension using the existing data while keeping claims proportional to the evidence.

## 5 AI Use Statement

This reference draft was generated with OpenAI Codex on October 7, 2026. The precise model variants for the current and earlier workflow must be completed from app metadata or transcripts. Codex retrieved the September 22 research conversation, read the assignment documents, checked stored analyses against the original materials, independently recalculated the headline attendance result, and drafted the prose, tables, figures, and alternative research memos. The underlying exploratory analysis was developed with AI assistance in the September 22 workflow. This statement discloses substantive drafting, not copyediting alone. Before submission, the author must revise the text, verify and understand the analysis, and complete the precise model versions, dates, tools, and human contributions from the retained transcripts. It does not claim that the author personally performed checks that are not documented.

[[PAGEBREAK]]

## References

Cameron, A. Colin, Jonah B. Gelbach, and Douglas L. Miller. 2008. "Bootstrap-Based Improvements for Inference with Clustered Errors." Review of Economics and Statistics 90 (3): 414-427. https://doi.org/10.1162/rest.90.3.414.

Duflo, Esther, Rema Hanna, and Stephen P. Ryan. 2012. "Incentives Work: Getting Teachers to Come to School." American Economic Review 102 (4): 1241-1278. https://doi.org/10.1257/aer.102.4.1241. Includes the official supplemental appendix and erratum linked from the journal page.

Duflo, Esther, Rema Hanna, and Stephen P. Ryan. 2019. "Replication Data for Incentives Work Getting Teachers to Come to School." Version 1. American Economic Association and Inter-university Consortium for Political and Social Research. Original data publication 2012; distribution date October 11, 2019. https://doi.org/10.3886/E112523V1.

Holm, Sture. 1979. "A Simple Sequentially Rejective Multiple Test Procedure." Scandinavian Journal of Statistics 6 (2): 65-70. https://www.jstor.org/stable/4615733.

[[PAGEBREAK]]

## Appendix A Fixed sensitivity analyses

[[TABLE robustness]]

Table A1 retains the main interaction beside three fixed checks. Geographic controls use the existing school block field on the same 2,195-child sample. They are geographic indicators; the analysis does not establish that they are randomization strata. The coefficient is 22.1 percentage points, with interval 8.2 to 36.0 points. The calendar check applies the same last-open-check rule using dates through December 31, 2005. Its coefficient is 19.7 points, with interval 4.8 to 34.6 points. Neither check supplies a treatment-independent participation measure.

The attendance-code sensitivity removes all 113 ambiguous departure classifications, leaving 2,082 children in 111 schools. Its interaction is 26.6 points, with interval 12.0 to 41.2 points and clustered p < .001. The wild-bootstrap p-value is .001. The excluded cases differ by assignment and baseline status, so this estimate is a selection sensitivity. Its larger magnitude is not a reason to replace the primary estimate.

[[TABLE measurement_bounds]]

Table A2 treats each flagged binary outcome as unknown and assigns all permissible zeros and ones within each cell. It reports the smallest and largest resulting writer-minus-nonwriter contrast. The attendance-code range is 16.3 to 34.1 points. The incomplete-history range is 11.9 to 36.4 points. Their union gives the broader range of 8.8 to 45.6 points. These are algebraic identification ranges conditional on the retained sample and all other recorded outcomes. They have no standard errors or p-values and are not confidence intervals. They do not bound every possible error in the roster or the counterfactual observation process.

## Appendix B Measurement and reconstruction details

The raw roster sources differ in the type of the departure-reason field. The main source stores it as text, while the appended source stores numbers. The distributed Stata append leaves the numeric source's reason values blank in the text column. The replication preserves that convention to match the original output. Mapping the raw numeric government-school code to its corresponding text marker changes 13 children's recorded destination classification in the 2,197-child replication cohort. It changes no total-departure indicators. This is a count comparison; the government-marker and residual interactions have not been re-estimated under that harmonized mapping. This is why total departure is the primary outcome and destinations remain secondary.

Across the selected rows in the consensus sample, 66.4 percent of reason fields are blank. Blanks constitute 69.9 percent in control and 63.3 percent in treatment. A blank is kept blank, and no unobserved destination is imputed. The residual measure is defined by absence of the recorded government-school marker within operational departure. It is not a direct observation of withdrawal from all education.

The original attendance recode maps several negative values and code 22 to zero. The package does not provide a codebook that establishes the meaning of each of those values. The sentinel audit flags operational departures with at least one such selected value. It identifies 28 control nonwriters, 11 control writers, 71 treatment nonwriters, and 3 treatment writers. These sum to 113. Of these children, 28 also have short observation histories. The remaining quality categories are 85 code-only cases, 117 history-only cases, and 1,965 children with neither documented flag.

The source sample remains fixed apart from the two conflicting baseline-writing records and the explicitly labeled exclusion check. No raw attendance, transfer-reason, or test-score observations are added. Calendar sensitivity and coding sensitivity are reported separately because they alter different parts of the measurement process. Neither is used to redefine the main result after seeing its significance.

## Appendix C Prior candidate directions and selection

The original teacher-score attendance catch-up story is already explicit in the paper and is not treated as a new contribution. The candidate learning-by-teacher-score extension is more distinct, but its observed-test total interaction is 0.132 standard deviations, with interval -0.009 to 0.273 and p = .067 in 1,625 source rows across 101 schools. Geographic controls reduce it to 0.087, with interval -0.042 to 0.217. Those source rows represent 1,610 unique school-child keys. The result does not establish a difference at the conventional two-sided 5 percent level.

The fixed learning-domain family gives a nominal mathematics interaction p-value of .037, but Holm adjustment across mathematics, language, and total yields .110 for mathematics. The direct mathematics-minus-language interaction has p = .054, and the joint domain test has p = .090. These results do not justify selecting mathematics alone as an established new effect.

The learning-distribution route uses 1,737 observed source rows, 1,720 unique school-child keys, and 107 schools. Its fixed lower-quartile contrast is 0.081 standard deviations, with a school-bootstrap percentile interval from -0.081 to 0.219 and approximate two-sided p = .310. The median, upper-quartile, and interquartile-range contrasts also have intervals containing zero. These analyses are retained as legitimate but inconclusive alternatives. Their existence is part of the departure paper's exploratory search history.

## Appendix D Reproducibility record

The source package is E112523V1. The original benchmark programs are Table1_Fig1_update.do, Table-2.do, and Table7_Table10.do, under data/Incentives_FINAL/Programs. The raw departure reconstruction is in scripts/audit_transition_extension.py; the interaction, clustered intervals, block check, endpoint check, and bootstrap are in scripts/audit_transition_scope.py. The documented-code flags and bounds are generated by scripts/audit_sentinel_measurement.py, while scripts/audit_transition_sentinels.py generates the exclusion sensitivity. The supplied Stata programs are source benchmarks, not evidence that Stata was run for this draft.

The main statistical outputs are transition_table10_reproduction.csv under outputs/research_direction_audit and transition_scope_group_effects.csv, transition_scope_model_results.csv, drop_wildbootstrap_summary.json, sentinel_complete_wildbootstrap_summary.json, and transition_incomplete_last5_bounds.csv under outputs/scope_search_2026_09_22/transition. The union bounds are in measurement/sentinel_interaction_bounds.json. Their raw-input hashes and direct-refit checks remain in the original analysis directories. The draft's exhibit builder reads these saved results and independently verified counts; it does not silently change the underlying analyses.

The October 7 attendance check used Python 3.13, NumPy 1.26.4, pandas 2.3.0, and SciPy 1.15.3. It recomputed the raw random-check coefficient and clustered covariance without writing to the original output files. The original analysis scripts provide the computational specification; a complete submission package should record its own pinned environment and a successful rerun. A README, rerun verifier, and exhibit builder accompany this reference draft locally. A public or shared replication URL and the author's identifying details have not been supplied and must be completed before submission.
