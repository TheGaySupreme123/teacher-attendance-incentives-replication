# Attendance Incentives and Recorded School Departure by Baseline Writing Status

[Author name]

## Abstract

Does assignment to a teacher attendance program change recorded school departure differently by children's baseline writing status? I replicate and extend Duflo, Hanna, and Ryan's randomized camera-monitoring and attendance-pay experiment in Rajasthan. The replication reproduces the main attendance effect and the average departure results. The extension interacts treatment assignment with baseline written-test status. Among 2,195 children in 111 schools, the departure effect is 5.0 percentage points for baseline nonwriters and 26.1 points for baseline writers. The difference is 21.1 points, with a school-clustered 95 percent confidence interval of 6.9 to 35.3 points. This exploratory result adds a preparation-group comparison to the original aggregate finding. Departure follows the original attendance-based rule. Treatment changes observation opportunities, and incomplete destination records prevent interpreting the interaction as withdrawal from education or as a transfer mechanism.

## 1 Introduction

Does a teacher attendance program change recorded departure from a nonformal school differently for children who could already take a written test? I examine this question in the randomized experiment of Duflo, Hanna, and Ryan (2012). I first reproduce the program's main attendance effect and its average departure results. I then extend the departure analysis by interacting treatment assignment with baseline written-test status. This comparison connects two parts of the original paper: its evidence on children's initial preparation and its evidence on leaving the original school.

The program increases recorded departure by 5.0 percentage points among baseline nonwriters and 26.1 points among baseline writers. The difference is 21.1 points, with a school-clustered 95 percent confidence interval of 6.9 to 35.3 points. The reconstructed aggregate Table 10 departure effect is 8.4 points; the published table reports 0.08. These estimates answer different questions: the aggregate describes the average treatment-control difference, while the interaction compares that difference across the two baseline groups. The contribution is an exploratory extension of the original participation analysis, rather than a revision of its teacher-attendance finding.

Teacher absence limits access to instruction. Unannounced visits to Indian government primary schools found about one-quarter of teachers absent and only about half teaching when observed (Kremer et al. 2005). Guerrero et al. (2013) find positive pooled attendance effects for monitoring with incentives in their review of nine experimental or quasi-experimental studies, but statistically inconclusive pooled achievement effects. Their limited evidence base and search ending in 2010 leave downstream outcomes open. Incentive design also matters. Kenyan test-score rewards increased rewarded examination performance and test preparation without increasing teacher attendance or performance on unrelated tests (Glewwe, Ilias, and Kremer 2010). Indian performance pay improved learning without an attendance change; classroom observations were consistent with greater effort conditional on presence (Muralidharan and Sundararaman 2011). These findings motivate distinguishing provider presence from children's subsequent participation.

Monitoring can affect both participation and its measurement. In Uganda, monitoring combined with a bonus increased teacher presence and improved reported information, whereas monitoring alone did not improve attendance. Enrollment gains were concentrated in schools where dropout was common. Changes in pupil composition complicated the learning comparison, and the authors' selection bounds included zero (Cilliers et al. 2018). Linden and Shastry (2012) document differences between teacher and external-monitor attendance records in a conditional grain program. Neither study establishes a problem in the Rajasthan records. Together, they show why an incentive program's effect on recorded participation requires attention to both institutional context and observation.

Initial preparation supplies a pre-treatment comparison with a clear connection to the original study. Remedial instruction in India produced its largest gains among initially low-scoring children (Banerjee et al. 2007). Kenyan tracking produced gains across the initial-achievement distribution, which the authors interpret as consistent with peer effects and teaching adapted to pupil level (Duflo, Dupas, and Kremer 2011). These studies motivate testing heterogeneity without predicting its sign. In Rajasthan, baseline writers took a written test, while nonwriters took an oral test. Duflo, Hanna, and Ryan (2012) report larger estimated learning gains among baseline writers, but Table 10 pools writing groups when reporting departure. In the article, supplement, erratum, and replication materials reviewed here, I do not find the departure interaction examined in this paper.

The endpoint limits interpretation. Recorded departure means zero attendance in the latest up to five observed checks at which the original school was open. Treatment increases school opening and therefore changes the opportunities to observe children. Leaving a nonformal center can also accompany progression into government school. The interaction consequently does not establish educational dropout or explain why children leave. Section 2 presents the experiment and replication. Section 3 develops the extension and its results. Section 4 concludes. Sensitivity analyses, measurement details, and the exploratory search history appear in the appendices.

## 2 Replication

### 2 1 Experimental setting and original findings

Duflo, Hanna, and Ryan (2012) ask whether daily attendance monitoring and attendance-linked pay reduce teacher absence and improve children's learning. They study single-teacher nonformal education centers operated by Seva Mandir in rural Udaipur, Rajasthan. The centers teach basic Hindi and mathematics and can prepare children to enter government schools. A teacher's absence normally closes the center. The experiment initially assigned 120 schools equally to treatment and control. Seven closed after randomization but before the program was announced, leaving 57 treatment and 56 control schools.

The program began in September 2003. The attendance analysis runs through February 2006; the program still operated as of October 2009 (Duflo, Hanna, and Ryan 2012, 1249, 1251). Only treatment schools used program cameras; a child photographed the teacher and pupils at each day's start and end. Camera records determined pay under a nonlinear attendance schedule, which could raise or lower the teacher's salary. Control teachers received fixed salaries. Unannounced research visits measured attendance in both groups. Random assignment identifies the package's effect, without isolating cameras, financial incentives, or teacher presence as a mediator.

Using unannounced visits, child attendance and destination records, and tests, the authors find that the program reduced teacher absence by about 21 percentage points and increased children's test scores by about 0.17 standard deviations. They also report about a 10-percentage-point increase in government-school entry. Their dynamic labor-supply model uses daily camera records, finds that teachers respond to financial incentives, and evaluates alternative pay schedules (Duflo, Hanna, and Ryan 2012, 1241–1244).

I replicate the main experimental attendance result (Table 2) from random school visits and the average departure outcomes (Table 10) from child attendance and recorded destinations. I extend the departure analysis by linking those outcomes to baseline written-test status and testing whether the treatment effect differs between writers and nonwriters. Selected Table 9 learning specifications provide an additional audit. This replication does not reestimate the structural model.

### 2 2 Data and reconstruction

I use version 1 of the public replication package, E112523V1 (Duflo, Hanna, and Ryan 2019). I reconstruct the selected results in Python from the original Stata data files and compare them with the published tables and distributed output. The supplied Stata programs serve as benchmarks; I did not execute them in Stata. Appendix D identifies the reconstruction scripts, saved results, and software record.

The attendance sample contains 3,071 random visits to 113 schools. I apply the original school exclusions and time construction, omit the pre-announcement baseline period, and regress school opening on an intercept and treatment assignment. The original construction assigns late-August checks to the September 2003 intervention period and continues through February 2006. I cluster standard errors by school.

For departure, I reconstruct the enrolled child roster from the two raw sources and link school-child identifiers to random checks and baseline records. The Table 10 program orders each child's open-school checks from newest to oldest and retains up to five. Departure equals one when recoded attendance sums to zero in this window. A zero means that the child is not classified as departed under this rule; it does not independently establish continuous enrollment. The replication retains the original attendance recodes and reason-field append convention, including their documented ambiguities. No destination is imputed when a reason is blank.

The reconstructed departure sample contains 2,197 children in 111 schools. The program also produces a government-school marker and a residual departure outcome. Under its coding, total departure is their sum. I use these operational labels because the absence of a government-school marker does not verify withdrawal from all education. Appendix B explains the missing reasons and the mismatch between numeric and text reason fields.

### 2 3 Replication results

[[TABLE replication]]

Table 1 reports both replications: original Table 2, Panel A, for attendance and original Table 10 for departure. Schools are open at 78.7 percent of treatment visits and 58.0 percent of control visits. The estimated difference is 0.207, with a clustered standard error of 0.030. Both round to the published values. The corresponding 95 percent confidence interval is 14.9 to 26.6 percentage points.

The departure rows in Table 1 also match the coefficients and standard errors in original Table 10 at their reported precision. Total recorded departure increases by 8.4 percentage points. The government-school marker increases by 10.1 points, and residual departure changes by -1.8 points. The reconstructed child outcomes agree with the distributed reference records. Matching these results establishes fidelity to the implemented measure, while leaving its educational interpretation open.

An additional learning audit matches 16 selected Table 9 specifications to the distributed coefficients, standard errors, and sample sizes. For example, the Panel A post-test total specification with child baseline-test controls gives 0.173, with standard error 0.087, in 1,760 source records. This check supports the original learning benchmark. The main extension below concerns departure, and the alternative learning analyses remain in Appendix C.

## 3 Extension

### 3 1 Baseline writing and the analysis sample

The extension adds baseline written-test status and its interaction with randomized treatment to the original departure model. The outcome and treatment assignment remain those of the replication; the analysis excludes two unresolved baseline-status conflicts, as described below. This design asks whether the package's recorded departure effect differs across a measured baseline characteristic. It does not estimate the causal effect of writing ability.

The comparison has a direct substantive basis. The original centers provide basic instruction and can serve as a route into government school. Children who could already take a written test may respond differently to additional instruction from children who took the oral baseline test. A larger departure response among writers could be consistent with progression beyond the center. It could also reflect other differences between the groups or the way participation is observed. The analysis therefore tests the difference without imposing a transfer or disengagement explanation.

I link the 2,197 reconstructed outcomes to baseline writing records by school and child identifier. Repeated baseline records must agree. Two eligible children have conflicting written-test status, so I exclude them rather than assign a category. The main sample contains 2,195 unique children in 111 schools: 1,136 in treatment and 1,059 in control, across 57 treatment and 54 control schools. There are 1,798 nonwriters and 397 writers. No new observations, external measures, or selected test-score thresholds enter the extension.

I use writer and nonwriter as labels for the baseline test protocol. Writers took the written baseline test; nonwriters did not. This binary measure captures one aspect of initial preparation. It does not define a permanent ability type or measure all dimensions of literacy. The same classification appears in the original attendance and learning analyses, which makes the new comparison closely tied to the original research design.

### 3 2 Empirical specification

For child i in school s, I estimate the saturated linear probability model

[[EQUATION departure]]

Y is recorded departure, T is school treatment assignment, and W is baseline written-test status. The treatment coefficient τ is the treatment-control difference for nonwriters. The sum τ plus δ is the corresponding difference for writers. The interaction δ is the writer treatment effect minus the nonwriter treatment effect. With both binary main effects and their interaction, equation 1 reproduces the four observed group means. Each child receives equal weight.

Treatment was assigned at school level, so I cluster the covariance matrix by the 111 schools. I use the audited implementation's finite-sample correction and t critical values with 110 degrees of freedom. The writer effect's uncertainty uses the covariance between the treatment and interaction estimates. I estimate the interaction directly because children from both baseline groups can attend the same school. Separate subgroup significance tests would not test equality of the two effects.

I report two additional inference procedures. A null-imposed wild-cluster bootstrap applies a common random sign to restricted-model residuals within each school and recomputes the interaction t statistic. It uses 9,999 Rademacher draws with seed 20260922, following the general approach of Cameron, Gelbach, and Miller (2008). Holm's (1979) procedure adjusts the three departure-related interaction p-values. This family includes total departure, the government-school marker, and residual departure. All three use the same sample and specification.

The direction was selected after examining other extensions. Clustered inference and the bootstrap describe uncertainty under the stated models. The Holm adjustment controls the specified three-outcome family, rather than the full earlier search. The result remains exploratory. Appendix C reports the prior candidate analyses so that the selection history is part of the evidence.

### 3 3 Treatment effects by baseline writing status

[[TABLE group_rates]]

Table 2 shows a larger treatment-control gap among writers: 26.1 percentage points, compared with 5.0 among nonwriters. Its cell counts and rates describe children in randomized schools, rather than before-after changes for the same children.

[[FIGURE main_effects]]

Figure 1 displays the two effects and their direct difference. The nonwriter effect has a 95 percent confidence interval of -2.4 to 12.4 points. The writer effect has an interval of 10.0 to 42.3 points. The interaction is 21.1 points, with clustered standard error 7.2 points and interval 6.9 to 35.3 points. Its clustered p-value is .004, its wild-bootstrap p-value is .007, and its Holm-adjusted p-value is .012.

The interaction, rather than the significance of either subgroup estimate alone, supplies the evidence for different responses. The nonwriter interval admits a positive effect above ten points as well as a small negative effect. It therefore does not establish that nonwriters are unaffected. Writers make up the smaller group, which is reflected in their wider interval. Even with this uncertainty, the directly estimated difference excludes zero under the reported clustered inference.

This comparison adds information that the original 8.4-point average does not provide. The 21.1-point interaction measures the additional writer response, rather than the average effect or the share of children induced to leave. The aggregate replication also retains the two records excluded from the extension. I keep the original coefficient and the new interaction separate because their samples and estimands differ.

### 3 4 Connection to the original child outcomes

Duflo, Hanna, and Ryan (2012) treat child presence, learning, and departure as distinct outcomes. Table 7 reports more instruction time because treatment schools open more often. Its baseline-test subgroup comparison uses children who did not leave the center, a sample selected on a post-treatment outcome. The presence point estimates are 14 percentage points for oral-pretest children and 10 for written-pretest children; their difference is not significant. Table 9 and its accompanying discussion report larger estimated learning gains for children who could take the written pretest. Table 10 pools the child sample when reporting leaving the NFE, government-school enrollment, and dropout. The extension crosses its operational total-departure measure with the baseline grouping used in the earlier tables.

These results address different margins. Table 7's subgroup presence comparison conditions on children who did not leave the center, while the departure analysis includes the reconstructed child cohort. The learning results also use their own observed-test samples. The new interaction consequently does not contradict the original presence comparison or show that the children who gained most in learning were the same children who later transferred. It identifies heterogeneity in the recorded departure outcome, without estimating a joint child-level pathway from attendance to learning to destination.

[[TABLE outcome_family]]

Table 3 examines whether the destination markers support a more specific interpretation. The government-school interaction is 4.8 percentage points, with a 95 percent interval of -10.5 to 20.2 points and p = .534. Residual departure has an interaction of 16.3 points, with interval 4.6 to 27.9 points and p = .007. Its Holm-adjusted p-value is .014, and its wild-bootstrap p-value is .010. Under the supplied coding, the two destination-component interactions sum to the total departure interaction.

The government-school interval does not establish a differential transfer effect for writers. The residual interaction also cannot establish educational harm. It classifies departures without the recorded government-school marker, including cases with missing destination information. The original paper's interpretation of aggregate government-school movement motivates the question, but it cannot supply an explanation for this new subgroup contrast. I report the complete family to make that limit visible.

### 3 5 Measurement and scope of inference

The central measurement concern follows directly from the intervention's success in opening schools. The departure rule selects the latest observed checks at which the school was open. Nonwriters average 15.4 open checks in control and 20.4 in treatment; writers average 15.2 and 21.9. Treatment therefore changes how often children can enter the attendance record. The last five open checks need not span the same calendar interval across arms or baseline groups.

Random assignment supports comparing the implemented classification. It does not make that classification a treatment-independent measure of permanent exit. A child with no recorded attendance in the selected window may have progressed, disengaged, or been absent during the particular checks observed. A child with some attendance is not independently verified as continuously enrolled. The interaction can reflect a change in participation, a change in its observation, or both. This ambiguity affects the educational interpretation even when the statistical difference is precise.

Two documented features further limit measurement. In the main sample, 145 children have fewer than five open checks, and 113 departure classifications involve attendance values whose meanings are not established by a supplied codebook. The sets overlap for 28 children, leaving 230 with either flag. Destination reasons are blank in 66.4 percent of selected records. I preserve the original conventions for replication and distinguish these limitations from sampling uncertainty.

Appendix A reports geographic controls, a December 2005 endpoint, exclusion of the ambiguous-code cases, and algebraic ranges that treat flagged outcomes as unknown. The interaction remains positive under these specified checks. The exclusion changes the analyzed population, and the algebraic ranges condition on the remaining observations. Neither resolves the treatment-dependent observation process or recovers missing destinations. The main claim is therefore a difference in recorded departure under the original roster rule, with exploratory inference and an unresolved educational interpretation.

## 4 Discussion and conclusion

The replication reproduces the main attendance effect and the average departure outcomes of Duflo, Hanna, and Ryan (2012). The extension finds a larger recorded departure response among children who took the written baseline test. Their treatment effect exceeds the nonwriter effect by 21.1 percentage points, with a school-clustered 95 percent confidence interval of 6.9 to 35.3 points.

This finding links the original departure analysis to a baseline preparation measure already used in its attendance and learning results. The same randomized package can increase observed school opening while changing recorded departure from the original center. The interaction adds a group comparison to that aggregate evidence. It leaves the original teacher-attendance result intact and does not identify writing ability or increased teacher presence as a mechanism.

The result's educational meaning remains uncertain. Treatment changes the open-school checks used to classify departure. Incomplete histories, undocumented attendance codes, and missing destinations compound that limitation. The reported sensitivities preserve a positive interaction under particular changes, but they do not establish permanent withdrawal from education or differential government-school transfer. The exploratory selection history also limits the interpretation of the reported p-values. Under the original operational measure, assignment changes recorded departure more for baseline writers than for nonwriters; the data do not establish why.

## 5 AI Use Statement

OpenAI Codex assisted the exploratory analysis on September 22, 2026, the reference drafting on October 7, the literature expansion using the Tel Aviv University catalogue on October 9, and this revision on October 12. It helped reconstruct code, check stored results against original materials, recalculate the attendance benchmark, review peer-reviewed sources, and draft and reorganize the prose and exhibits. This statement discloses substantive AI drafting as well as analysis assistance. It does not describe the work as copyediting alone or claim that the human author performed all computational checks. The retained conversations document the workflow. Exact model identifiers for the earlier sessions and the author's subsequent revisions remain to be completed in the author's final version.

[[PAGEBREAK]]

## References

Banerjee, Abhijit V., Shawn Cole, Esther Duflo, and Leigh Linden. 2007. "Remedying Education: Evidence from Two Randomized Experiments in India." Quarterly Journal of Economics 122 (3): 1235-1264. https://doi.org/10.1162/qjec.122.3.1235.

Cameron, A. Colin, Jonah B. Gelbach, and Douglas L. Miller. 2008. "Bootstrap-Based Improvements for Inference with Clustered Errors." Review of Economics and Statistics 90 (3): 414-427. https://doi.org/10.1162/rest.90.3.414.

Cilliers, Jacobus, Ibrahim Kasirye, Clare Leaver, Pieter Serneels, and Andrew Zeitlin. 2018. "Pay for Locally Monitored Performance? A Welfare Analysis for Teacher Attendance in Ugandan Primary Schools." Journal of Public Economics 167: 69-90. https://doi.org/10.1016/j.jpubeco.2018.04.010.

Duflo, Esther, Pascaline Dupas, and Michael Kremer. 2011. "Peer Effects, Teacher Incentives, and the Impact of Tracking: Evidence from a Randomized Evaluation in Kenya." American Economic Review 101 (5): 1739-1774. https://doi.org/10.1257/aer.101.5.1739.

Duflo, Esther, Rema Hanna, and Stephen P. Ryan. 2012. "Incentives Work: Getting Teachers to Come to School." American Economic Review 102 (4): 1241-1278. https://doi.org/10.1257/aer.102.4.1241. Includes the official supplemental appendix and erratum linked from the journal page.

Glewwe, Paul, Nauman Ilias, and Michael Kremer. 2010. "Teacher Incentives." American Economic Journal: Applied Economics 2 (3): 205-227. https://doi.org/10.1257/app.2.3.205.

Guerrero, Gabriela, Juan León, Mayli Zapata, and Santiago Cueto. 2013. "Getting Teachers Back to the Classroom. A Systematic Review on What Works to Improve Teacher Attendance in Developing Countries." Journal of Development Effectiveness 5 (4): 466-488. https://doi.org/10.1080/19439342.2013.864695.

Holm, Sture. 1979. "A Simple Sequentially Rejective Multiple Test Procedure." Scandinavian Journal of Statistics 6 (2): 65-70. https://www.jstor.org/stable/4615733.

Kremer, Michael, Nazmul Chaudhury, F. Halsey Rogers, Karthik Muralidharan, and Jeffrey Hammer. 2005. "Teacher Absence in India: A Snapshot." Journal of the European Economic Association 3 (2-3): 658-667. https://doi.org/10.1162/jeea.2005.3.2-3.658.

Linden, Leigh L., and Gauri Kartini Shastry. 2012. "Grain Inflation: Identifying Agent Discretion in Response to a Conditional School Nutrition Program." Journal of Development Economics 99 (1): 128-138. https://doi.org/10.1016/j.jdeveco.2011.11.002.

Muralidharan, Karthik, and Venkatesh Sundararaman. 2011. "Teacher Performance Pay: Experimental Evidence from India." Journal of Political Economy 119 (1): 39-77. https://doi.org/10.1086/659655.

### Data source

Duflo, Esther, Rema Hanna, and Stephen P. Ryan. 2019. "Replication Data for Incentives Work Getting Teachers to Come to School." Version 1. American Economic Association and Inter-university Consortium for Political and Social Research. Original data publication 2012; distribution date October 11, 2019. https://doi.org/10.3886/E112523V1. This dataset citation records empirical provenance and is separate from the peer-reviewed literature.

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
