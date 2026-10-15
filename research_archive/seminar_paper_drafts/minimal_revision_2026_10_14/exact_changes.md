# Exact edits to your replication and extension

The clean DOCX revises only the supplied Sections 2–3. Original source files and the prior reference paper remain unchanged. This log records every local prose substitution. The equation is native Word math; the placeholder exhibits use saved verified results.

The table transcription was moved to Table 3, expanded to the stated three-outcome family, and given complete inference notes. Tables 1–2 and Figure 1 fill the original exhibit references. Four pasted footnote markers and existing appendix references are retained for integration with the complete manuscript; their unprovided contents were not invented.

Original prose word tokens retained in order: 2108/2770 (76.1%); this measure excludes the equation and exhibits. It is a token-preservation metric, not a claim that every retained sentence is unchanged.

## Edit 1 at source line 1
Remove editor metadata from manuscript title.

Before:  (edited)
After: [deleted]

## Edit 2 at source line 2
Remove editor metadata from manuscript body.

Before: Oct 14, 2026 · @Shay
After: [deleted]

## Edit 3 at source line 5
State original question and headline findings before the selected replication.

Before: study whether monitoring affects teacher absenteeism.
After: study whether camera monitoring and attendance-linked pay reduce teacher absenteeism and improve learning. They find about a 21-percentage-point reduction in teacher absence and a 0.17-standard-deviation gain in test scores.

## Edit 4 at source line 5
Identify the randomized package.

Before: randomize schools to monitoring via photographs
After: randomize schools to a package of camera monitoring and attendance-linked pay

## Edit 5 at source line 6
Clarify research measurement in both arms.

Before: the control group continued to receive surprise visits from researchers
After: researchers measured attendance through surprise visits in both treatment and control schools

## Edit 6 at source line 7
Separate dataset provenance from the journal article.

Before: Duflo, Hanna and Ryan in a replication package (E112523V1) which consisted
After: Duflo, Hanna and Ryan (2019) in a replication package (E112523V1), which consists

## Edit 7 at source line 7
Limit replication claim to actually reproduced results.

Before: the paper’s Table 2 (which includes main results) and Table 10 (which reports effects on average departure)
After: the pooled all-teacher result in the paper’s original Table 2, Panel A, and all three departure rows in its Table 10

## Edit 8 at source line 7
Provide a concise reproducibility pointer to the existing full-paper appendix.

Before: in Python.
After: in Python. Software and reproduction details appear in Appendix D.

## Edit 9 at source line 7
Avoid an implication of unassisted work.

Before: continue with the extension on my own
After: add the extension described below

## Edit 10 at source line 8
Distinguish original tables from the new tables.

Before: In Table 2,
After: In the original Table 2, Panel A,

## Edit 11 at source line 9
Specify selected attendance replication.

Before: I match the results in Table 2 of
After: I match the pooled result in the original Table 2, Panel A, of

## Edit 12 at source line 9
Distinguish finer reconstruction precision from the published values.

Before: As in the original table, schools were open
After: In my reconstruction, schools were open

## Edit 13 at source line 9
Align wording and SE display.

Before: with SEs clustered at the school level in parentheses, is 0.207, SE 0.030
After: with SEs clustered at the school level in parentheses, is 0.207 (0.030)

## Edit 14 at source line 9
Do not claim reproduction of every Table 2 specification.

Before: I match all results
After: I match these published values

## Edit 15 at source line 9
Supply CI units and refer to the actual replication exhibit.

Before: [14.9, 26.6].
After: [14.9, 26.6] percentage points. Table 1 reports both the attendance and departure replications.

## Edit 16 at source line 9
Make the conversion from the probability-unit coefficient explicit.

Before: The 95% confidence interval is [14.9, 26.6] percentage points.
After: Expressed in percentage points, the 95% confidence interval is [14.9, 26.6].

## Edit 17 at source line 10
Repair subject-verb agreement.

Before: and report standard errors
After: and reports standard errors

## Edit 18 at source line 10
Account for incomplete observed histories.

Before: select the last five times they were checked
After: select the latest up to five times they were checked

## Edit 19 at source line 10
Keep the rule consistent for children with fewer than five checks.

Before: in those five instances
After: in those selected instances

## Edit 20 at source line 10
Qualify the operational endpoint.

Before: then this child has left
After: then this child is classified as having departed under this rule

## Edit 21 at source line 10
Include all three original Table 10 outcome rows.

Before: The dependent variables are (1) an indicator for departure and (2) an indicator for departure for which we know the child moved to a government school.
After: The dependent variables are (1) recorded departure, (2) a government-school marker among recorded departures, and (3) residual departure, equal to recorded departure minus the marker.

## Edit 22 at source line 11
Correct the implemented join keys.

Before: These files provide information on school id × child id and can be merged on to random checks using these identifiers and on to baseline data using these identifiers and random check time period = baseline.
After: I merge these roster files on to school random checks using school id and visit date, and on to child enrollment and baseline writing records using school id × child id.

## Edit 23 at source line 11
Identify actual ambiguities precisely.

Before: Although parts of this process are unclear to me,
After: Some attendance codes lack documented meanings, and the reason fields differ in type.

## Edit 24 at source line 11
Separate attendance classification from reason markers.

Before: In many instances the departure reason is blank; I code these as having left but the destination unknown.
After: In many instances the reason is blank; a blank does not itself classify a child as departed or supply a government-school marker. The marker equals one for a child classified as departed with reason “2” in at least one selected record.

## Edit 25 at source line 11
Avoid claiming verified transfers.

Before: whether we know a child went to government school
After: the recorded government-school marker

## Edit 26 at source line 11
Define the recorded rather than independently verified endpoint.

Before: whether or not we know that a child went to a government school
After: whether the selected records contain a government-school reason marker

## Edit 27 at source line 12
Retain supported significance while qualifying endpoints and showing uncertainty.

Before: Treatment causes a statistically significant 8.4pp increase in departure, and a 10.1pp increase in departure to government schools.
After: Assignment to the bundled program causes a statistically significant 8.4-percentage-point increase in recorded departure (SE 4.1 points, p = .044), and a 10.1-point increase in the government-school marker (SE 3.5 points).

## Edit 28 at source line 12
Use explicit percentage-point units.

Before: a 10.1-point increase
After: a 10.1-percentage-point increase

## Edit 29 at source line 13
Provide consistent units and uncertainty.

Before: −1.8 point change in residual departure.
After: −1.8-percentage-point change in residual departure (SE 3.1 points, p = .564).

## Edit 30 at source line 13
Limit the matching claim to verified endpoints.

Before: all child-level reference values
After: the child-level departure indicators

## Edit 31 at source line 16
Retain motivation while qualifying the proxy.

Before: children who were better prepared to enter government schools (as proxied by participating in the written baseline test)
After: children who were better prepared to enter government schools (with written baseline-test status used as a coarse preparation proxy)

## Edit 32 at source line 16
State the interaction estimand and avoid an unobserved dropout claim.

Before: whether writers and nonwriters differ in departures, regardless of whether those departures are due to entry to government schools or drop-out from education more broadly
After: whether the treatment effect on recorded departure differs between writers and nonwriters, with or without a government-school marker

## Edit 33 at source line 17
Remove inconsistent table number before the equation.

Before: In Table 4, I estimate
After: I estimate

## Edit 34 at source line 18
Replace with the actual saturated model.

Before: Y_{isc} = \alpha_s + \gamma_{sc} + \lambda_c + \tau_{isc} \times T_{sc} + \delta_{isc} \times (W_{ic} \times T_{sc}) + \varepsilon_{ics} \qquad (1)
After: Y_{is} = \alpha + \tau T_s + \beta W_{is} + \delta(T_s \times W_{is}) + \varepsilon_{is} \qquad (1)

## Edit 35 at source line 19
Use common coefficients and the corrected four cell means.

Before: α_s + γ_sc + τ_isc + δ_isc
After: α + β + τ + δ

## Edit 36 at source line 19
Use common coefficients and the corrected four cell means.

Before: α_s + γ_sc
After: α + β

## Edit 37 at source line 19
Use common coefficients and the corrected four cell means.

Before: α_s + τ_isc
After: α + τ

## Edit 38 at source line 19
Use common coefficients and the corrected four cell means.

Before: α_s
After: α

## Edit 39 at source line 19
The same equation is fitted to each of the three defined outcomes.

Before: Y is an indicator for departure
After: Y is the binary outcome being analyzed

## Edit 40 at source line 19
Clarify the covariance calculation without a sentence fragment.

Before: Standard errors clustered
After: School-clustered standard errors

## Edit 41 at source line 19
Avoid repeating the clustering level.

Before:  at the school level
After: [deleted]

## Edit 42 at source line 19
Identify the variance of the writer linear combination.

Before: account for covariance with δ
After: account for covariance between τ and δ

## Edit 43 at source line 20
Prepare for the later complete Table 3 exhibit.

Before: The table reports three different outcomes in Y.
After: I estimate the model for three different outcomes in Y.

## Edit 44 at source line 20
Use the actual recorded government marker.

Before: known to be attending a government school at follow-up
After: classified as departed and has a government-school reason marker in at least one selected record

## Edit 45 at source line 20
Correct the bootstrap procedure and typo.

Before: follow-up-up 9,999 Rademacher randomization draws
After: use 9,999 school-level Rademacher wild-bootstrap-t draws

## Edit 46 at source line 20
Correct the tested coefficient and which p-values receive Holm adjustment.

Before: The table reports wild bootstrap p-values for τ + δ (the departure rate differential for “Writers” relative to “nonwriters”) adjusted for multiple hypothesis testing using the procedure of Holm (1979).
After: The null sets δ = 0 while leaving the treatment and writing main effects unrestricted. Table 3 reports p-values for δ, the writer-minus-nonwriter difference in treatment effects. I adjust the conventional school-clustered p-values across the three outcomes using Holm (1979), and report wild-bootstrap p-values separately.

## Edit 47 at source line 40
Remove the false attribution and sentence fragment.

Before: and Duflo, Hanna and Ryan (2012) report it as exploratory. 
After: [deleted]

## Edit 48 at source line 40
Keep proxy language consistent.

Before: these children as high achievers
After: baseline writers as better prepared

## Edit 49 at source line 40
Correct the residual-category comparison.

Before: , any more than residual departure is actually a residual category.
After: . Residual departure is an operational residual category, not a measure of educational dropout.

## Edit 50 at source line 43
Remove the duplicated aggregate replication paragraph already covered in Section 2.

Before: I replicate the original paper’s estimate that monitoring caused children to leave Seva Mandir-run educational centers at higher rates (Duflo, Hanna and Ryan (2012) table 10 (E112523V1)). My reconstruction of their dependent variable Leaving the center shows an estimated treatment effect of 8.4 percentage points, as did the original study, matching the coefficients and standard errors in the original Table 10 at their reported precision.
After: [deleted]

## Edit 51 at source line 44
The extension uses the test protocol, not a score.

Before: based on their performance in a baseline test
After: by their baseline written-versus-oral test status

## Edit 52 at source line 44
Use journal-table references rather than the dataset identifier.

Before: tables 7 and 9 (E112523V1)
After: Tables 7 and 9

## Edit 53 at source line 44
Consistent table labeling.

Before: (table 7)
After: (Table 7)

## Edit 54 at source line 44
Consistent table labeling.

Before: (table 9)
After: (Table 9)

## Edit 55 at source line 44
Use the original journal table as the reference.

Before: table 10 on leaving the center (E112523V1)
After: Table 10 on leaving the center

## Edit 56 at source line 45
Remove repeated model, clustering, and bootstrap description already stated above.

Before: For this exploratory analysis, I interact treatment with being able to take the written (versus oral) pretest on my reconstruction of their leaving-the-center dependent variable. As before, I cluster by school, estimate an OLS model as in equation (1), and use the wild-cluster bootstrap suggested by Cameron, Gelbach and Miller (2008).
After: [deleted]

## Edit 57 at source line 46
Clarify the aggregate estimand and source table.

Before: the original table’s coefficient
After: the original Table 10 average recorded-departure coefficient

## Edit 58 at source line 46
Columns 2–3 contain tau and tau+delta rather than two interactions.

Before: an interaction analysis
After: group treatment effects from the interaction model

## Edit 59 at source line 46
Fix the sample arithmetic.

Before: I leave out the two children in my sample of 2,195 who happened to be included in my replication of their reported average.
After: I leave out the two children with conflicting baseline writing records from the 2,197-child replication sample, leaving 2,195 for the interaction analysis.

## Edit 60 at source line 46
Remove the contradiction and false noncomparability claim.

Before: I do not report the original coefficient and this new coefficient together because (a) they use slightly different samples, (b) the standard errors would not be comparable because these columns 2 and 3 are interactions, and (c) they are substantively different:
After: I report the estimates together with their sample sizes and school-clustered uncertainty. They use slightly different samples and answer different questions:

## Edit 61 at source line 46
Use the measured subgroup variable.

Before: by performance on a baseline test
After: by baseline written-test status

## Edit 62 at source line 46
Explain the included coefficient plot.

Before: Figure 1 graphs the results of columns 2–3.
After: Figure 1 graphs the results of columns 2–3 and their direct difference.

## Edit 63 at source line 47
Use child test-status labels.

Before: children who could write (“Writer” column)
After: baseline writers (“Writer” column)

## Edit 64 at source line 47
Use child test-status labels.

Before: children who could not (“nonwriter” column)
After: baseline nonwriters (“Nonwriter” column)

## Edit 65 at source line 47
Use child test-status labels.

Before: children who could not write as unaffected
After: baseline nonwriters as unaffected

## Edit 66 at source line 47
Use child test-status labels.

Before: children who could write had a 21.1
After: baseline writers had a 21.1

## Edit 67 at source line 47
State interaction units.

Before: point larger effect
After: percentage-point larger effect

## Edit 68 at source line 47
Use child test-status labels.

Before: children who could not.
After: baseline nonwriters.

## Edit 69 at source line 47
Do not attribute the added bootstrap to the original article.

Before: , as in the original paper
After: [deleted]

## Edit 70 at source line 48
The recorded marker supplies some destination information, so avoid saying none exists.

Before: This analysis says nothing about why or where these children went when they left:
After: The total-departure interaction does not establish why or where these children went when they left:

## Edit 71 at source line 48
Use accurate variable levels.

Before: Treatment_i and Writer_i
After: school treatment and child baseline writing status

## Edit 72 at source line 48
Consistent table labeling.

Before: in table 3
After: in Table 3

## Edit 73 at source line 48
Avoid an untested contrast claim and an ability measure claim.

Before: The interaction with baseline ability is much larger on Departure: residual than on Government school
After: The interaction with baseline writing status has a larger point estimate on Residual departure than on Government school

## Edit 74 at source line 49
Repair sentence grammar and distinguish selected-stayer Panel C from the full table.

Before: Results do not contradict those reported in the original study’s table 7, which found that more hours of instruction due to more days that the school was open (Duflo, Hanna and Ryan (2012) table 7 (E112523V1)), because this table limits its analysis to children who stayed at the center and reports
After: Results do not contradict those reported in the original study’s Table 7, which found more hours of instruction because schools were open more often. Panel C limits its analysis to children who stayed at the center and reports

## Edit 75 at source line 49
The original article does not test equality of these subgroup learning effects.

Before: the original table 9 finds that children who could take the written pretest had significantly higher gains in learning
After: the original Table 9 reports larger estimated learning gains among children who took the written pretest

## Edit 76 at source line 49
Original Table 7 reports instruction days rather than hours.

Before: more hours of instruction
After: more days of instruction

## Edit 77 at source line 49
Consistent new-versus-original table references.

Before: My results in table 2 extend the original study’s table 10
After: My results in Table 2 extend the original study’s Table 10

## Edit 78 at source line 49
Consistent table labeling.

Before: tables 7 and 9.
After: Tables 7 and 9.

## Edit 79 at source line 51
Identify all three interaction outcomes.

Before: Table 3 shows results for departure from baseline school and departure to government school
After: Table 3 shows interaction results for total recorded departure, the government-school marker, and residual departure

## Edit 80 at source line 51
State the correct decomposition.

Before: Under these definitions, the first two sum to departure as coded originally.
After: Under these definitions, the government-marker and residual interaction point estimates sum to the total-departure interaction.

## Edit 81 at source line 51
The delta test compares two treatment effects.

Before: writers were more likely to move into government schools
After: the treatment effect on the recorded government-school marker was larger for writers than nonwriters

## Edit 82 at source line 51
Avoid implying missing reasons or attendance automatically create departure.

Before: Departure without a government school flag includes all other departures, including missing.
After: Departure without a government-school flag includes all other recorded departures, including those with missing destination reasons.

## Edit 83 at source line 51
Do not rule out transfers from a nonsignificant interaction.

Before: such a pattern is not able to explain the difference between the groups
After: the imprecise marker interaction and missing destination records do not establish whether transfers explain the difference between the groups

## Edit 84 at source line 52
Correct the type of ambiguous code.

Before: some have a coded reason for departure that does not appear in the available codebooks
After: some departure classifications involve undocumented attendance codes

## Edit 85 at source line 52
Keep the 113-case denominator but correct its meaning.

Before: 113 with unknown codes
After: 113 whose departure classifications involve undocumented attendance codes

## Edit 86 at source line 52
Do not claim verified randomization strata.

Before: region of baseline school
After: existing school-block/geographic indicators

## Edit 87 at source line 52
Correct the fixed endpoint rationale.

Before: (to minimize the observations with fewer than five checks)
After: (to check dependence on the final January–February 2006 records, whose appended reason values become blank under the distributed Stata convention)

## Edit 88 at source line 52
Correct the exclusion sensitivity.

Before: children with departure coded in a way not in the codebooks
After: the 113 children with ambiguous attendance-based departure classifications

## Edit 89 at source line 52
Separate measurement ranges from sampling uncertainty.

Before: bounding relies on other observations in the sample
After: the algebraic ranges hold the other observations fixed and are not confidence intervals

## Edit 90 at source line 53
Writer/nonwriter is a child characteristic.

Before: children in control (treatment) who went to schools run by nonwriters
After: baseline nonwriter children in control (treatment)

## Edit 91 at source line 53
Writer/nonwriter is a child characteristic.

Before: children who went to schools run by writers
After: baseline writer children

## Edit 92 at source line 53
Writer/nonwriter is not a principal characteristic.

Before: whether its principal was a writer
After: the child’s baseline writing status

## Edit 93 at source line 53
Clarify the observation-process limitation.

Before: common treatment-proof measure of exiting education
After: treatment-independent measure of permanent educational exit

## Edit 94 at source line 53
Specify zero attendance, including incomplete histories, rather than merely less-than-perfect attendance.

Before: A child not present in all five checks
After: A child absent at all selected checks

## Edit 95 at source line 53
Identify the check-level denominator, not a child-level proportion.

Before: across the sample chosen, the reason for departure is missing for 66.4% of observations
After: reason fields are blank in 7,112 of 10,707 selected open-school check records (66.4%)

## Edit 96 at source line 53
Correct the final child-level conclusion.

Before: children who went to schools run by writers than nonwriters
After: baseline writers than baseline nonwriters

## Edit 97 at source line 5
Consistent author-name punctuation.

Before: Duflo, Hanna and Ryan (2012) study whether camera monitoring and attendance-linked pay reduce teacher absenteeism and improve learning. They find about a 21-percentage-point reduction in teacher absence and a 0.17-standard-deviation gain in test scores. They run a field experiment with educational centers run by Seva Mandir in rural Udaipur, Rajasthan (Duflo, Hanna and Ryan, 2012). In these centers, which I will refer to as schools following the practice in Duflo, Hanna and Ryan (2012), children learn basic Hindi and other things to prepare them for enrolling in government schools. Schools typically have a single teacher, so are closed when the teacher is not present. Duflo, Hanna and Ryan (2012) randomize schools to a package of camera monitoring and attendance-linked pay; the treatment began in September 2003. I focus on results through February 2006, which was used to produce the two tables that I replicate; however, as of October 2009 the program was still active.¹
After: Duflo, Hanna, and Ryan (2012) study whether camera monitoring and attendance-linked pay reduce teacher absenteeism and improve learning. They find about a 21-percentage-point reduction in teacher absence and a 0.17-standard-deviation gain in test scores. They run a field experiment with educational centers run by Seva Mandir in rural Udaipur, Rajasthan (Duflo, Hanna, and Ryan, 2012). In these centers, which I will refer to as schools following the practice in Duflo, Hanna, and Ryan (2012), children learn basic Hindi and other things to prepare them for enrolling in government schools. Schools typically have a single teacher, so are closed when the teacher is not present. Duflo, Hanna, and Ryan (2012) randomize schools to a package of camera monitoring and attendance-linked pay; the treatment began in September 2003. I focus on results through February 2006, which was used to produce the two tables that I replicate; however, as of October 2009 the program was still active.¹

## Edit 98 at source line 5
Consistent Chicago author-date citation.

Before: (Duflo, Hanna, and Ryan, 2012)
After: (Duflo, Hanna, and Ryan 2012)

## Edit 99 at source line 6
Consistent author-name punctuation.

Before: Duflo, Hanna and Ryan (2012) randomize 120 schools, seven of which were excluded from the analysis following randomization but before the intervention was announced to schools, leaving 57 treatment and 56 control schools. In treatment schools, teachers and children were photographed at the beginning and end of each school day; researchers measured attendance through surprise visits in both treatment and control schools. Treatment schools' teachers were compensated based in part on attendance as indicated in the photos; control schools' teachers continued to receive a fixed wage.
After: Duflo, Hanna, and Ryan (2012) randomize 120 schools, seven of which were excluded from the analysis following randomization but before the intervention was announced to schools, leaving 57 treatment and 56 control schools. In treatment schools, teachers and children were photographed at the beginning and end of each school day; researchers measured attendance through surprise visits in both treatment and control schools. Treatment schools' teachers were compensated based in part on attendance as indicated in the photos; control schools' teachers continued to receive a fixed wage.

## Edit 100 at source line 7
Consistent author-name punctuation.

Before: Using data shared by Duflo, Hanna and Ryan (2019) in a replication package (E112523V1), which consists of Stata files, I replicate the pooled all-teacher result in the paper’s original Table 2, Panel A, and all three departure rows in its Table 10,² and recreate these results and an extension (described below) in Python. Software and reproduction details appear in Appendix D. After completing this replication, I add the extension described below.
After: Using data shared by Duflo, Hanna, and Ryan (2019) in a replication package (E112523V1), which consists of Stata files, I replicate the pooled all-teacher result in the paper’s original Table 2, Panel A, and all three departure rows in its Table 10,² and recreate these results and an extension (described below) in Python. Software and reproduction details appear in Appendix D. After completing this replication, I add the extension described below.

## Edit 101 at source line 8
Consistent author-name punctuation.

Before: In the original Table 2, Panel A, the sample consists of 3,071 random visits to 113 schools. Duflo, Hanna and Ryan (2012) estimate a regression of whether the school was open on a constant and treatment status and report standard errors clustered by school. To construct the data, I exclude a baseline period before treatment was announced, continue to exclude the same schools as Duflo, Hanna and Ryan (2012), and categorize the data collected in late August as belonging to the intervention period of September 2003–February 2006.
After: In the original Table 2, Panel A, the sample consists of 3,071 random visits to 113 schools. Duflo, Hanna, and Ryan (2012) estimate a regression of whether the school was open on a constant and treatment status and report standard errors clustered by school. To construct the data, I exclude a baseline period before treatment was announced, continue to exclude the same schools as Duflo, Hanna, and Ryan (2012), and categorize the data collected in late August as belonging to the intervention period of September 2003–February 2006.

## Edit 102 at source line 9
Consistent author-name punctuation.

Before: I match the pooled result in the original Table 2, Panel A, of Duflo, Hanna and Ryan (2012). In my reconstruction, schools were open in 78.7% of visits in treatment schools and 58.0% of visits in control schools. The estimated treatment effect, with SEs clustered at the school level in parentheses, is 0.207 (0.030). Rounding to match precision in the published table, I match these published values. Expressed in percentage points, the 95% confidence interval is [14.9, 26.6]. Table 1 reports both the attendance and departure replications.
After: I match the pooled result in the original Table 2, Panel A, of Duflo, Hanna, and Ryan (2012). In my reconstruction, schools were open in 78.7% of visits in treatment schools and 58.0% of visits in control schools. The estimated treatment effect, with SEs clustered at the school level in parentheses, is 0.207 (0.030). Rounding to match precision in the published table, I match these published values. Expressed in percentage points, the 95% confidence interval is [14.9, 26.6]. Table 1 reports both the attendance and departure replications.

## Edit 103 at source line 10
Consistent author-name punctuation.

Before: In Table 10 of Duflo, Hanna and Ryan (2012), the sample consists of 2,197 children in 111 schools. I match the results in Table 10, which includes regressions of departure indicators on a constant and treatment status and reports standard errors clustered by school. I use the algorithm in Duflo, Hanna and Ryan (2012): for a given child, first select the latest up to five times they were checked when the school was open, from last to first. Next, recode whether or not they attended in those selected instances, and sum up these recodes. If the result is 0, then this child is classified as having departed under this rule. A child for which this is not true did not necessarily continue; this method of aggregation does not tell us that. The dependent variables are (1) recorded departure, (2) a government-school marker among recorded departures, and (3) residual departure, equal to recorded departure minus the marker.
After: In Table 10 of Duflo, Hanna, and Ryan (2012), the sample consists of 2,197 children in 111 schools. I match the results in Table 10, which includes regressions of departure indicators on a constant and treatment status and reports standard errors clustered by school. I use the algorithm in Duflo, Hanna, and Ryan (2012): for a given child, first select the latest up to five times they were checked when the school was open, from last to first. Next, recode whether or not they attended in those selected instances, and sum up these recodes. If the result is 0, then this child is classified as having departed under this rule. A child for which this is not true did not necessarily continue; this method of aggregation does not tell us that. The dependent variables are (1) recorded departure, (2) a government-school marker among recorded departures, and (3) residual departure, equal to recorded departure minus the marker.

## Edit 104 at source line 11
Consistent author-name punctuation.

Before: I recreate this data on departure from the two raw data files. I merge these roster files on to school random checks using school id and visit date, and on to child enrollment and baseline writing records using school id × child id. To determine departure, I follow the procedure above. Some attendance codes lack documented meanings, and the reason fields differ in type. I follow the attendance recodes in Duflo, Hanna and Ryan (2012) as well as their procedure for appending reason variables. In many instances the reason is blank; a blank does not itself classify a child as departed or supply a government-school marker. The marker equals one for a child classified as departed with reason “2” in at least one selected record. I divide departure up into an indicator for the recorded government-school marker and an indicator for residual departure; these two outcomes sum to departure in my calculations. I chose the names of these categories carefully; the first is only a marker for whether the selected records contain a government-school reason marker, and not having this marker does not necessarily indicate leaving education. Appendix B describes this data more fully and discusses some inconsistencies between the numeric version of reasons children leave and a text version of these reasons.
After: I recreate this data on departure from the two raw data files. I merge these roster files on to school random checks using school id and visit date, and on to child enrollment and baseline writing records using school id × child id. To determine departure, I follow the procedure above. Some attendance codes lack documented meanings, and the reason fields differ in type. I follow the attendance recodes in Duflo, Hanna, and Ryan (2012) as well as their procedure for appending reason variables. In many instances the reason is blank; a blank does not itself classify a child as departed or supply a government-school marker. The marker equals one for a child classified as departed with reason “2” in at least one selected record. I divide departure up into an indicator for the recorded government-school marker and an indicator for residual departure; these two outcomes sum to departure in my calculations. I chose the names of these categories carefully; the first is only a marker for whether the selected records contain a government-school reason marker, and not having this marker does not necessarily indicate leaving education. Appendix B describes this data more fully and discusses some inconsistencies between the numeric version of reasons children leave and a text version of these reasons.

## Edit 105 at source line 14
Consistent author-name punctuation.

Before: The estimates below use the main sample described in Duflo, Hanna and Ryan (2012). To facilitate matching to the study replication files, I drop two children with multiple baseline observations whose records disagree about the child’s test status, resulting in 2,195 children from 111 schools. The sample includes 1,136 children from 57 treated schools and 1,059 children from 54 control schools. Without adding data or measures or imposing passing score cutoffs on test scores, there are 1,798 “nonwriters” and 397 “writers.”
After: The estimates below use the main sample described in Duflo, Hanna, and Ryan (2012). To facilitate matching to the study replication files, I drop two children with multiple baseline observations whose records disagree about the child’s test status, resulting in 2,195 children from 111 schools. The sample includes 1,136 children from 57 treated schools and 1,059 children from 54 control schools. Without adding data or measures or imposing passing score cutoffs on test scores, there are 1,798 “nonwriters” and 397 “writers.”

## Edit 106 at source line 16
Consistent author-name punctuation.

Before: A motivation for studying departures is that the Seva Mandir-operated centers can be stepping-stones towards enrollment into government schools by teaching children foundational skills. One reason treatment may have had heterogeneous effects on departures may be that it caused children who were better prepared to enter government schools (with written baseline-test status used as a coarse preparation proxy) to be more likely to leave the centers. Of course, any heterogeneity in departures could be due to a variety of other reasons, including other differences between writers and nonwriters or differential impacts of monitoring on measurement of writer versus nonwriter attendance. Duflo, Hanna and Ryan (2012) use this same distinction to analyze heterogeneous impacts of treatment on learning outcomes and attendance. This exercise examines whether the treatment effect on recorded departure differs between writers and nonwriters, with or without a government-school marker. Thus, these results should be viewed as exploratory, and do not estimate a treatment effect of ability or of writing.
After: A motivation for studying departures is that the Seva Mandir-operated centers can be stepping-stones towards enrollment into government schools by teaching children foundational skills. One reason treatment may have had heterogeneous effects on departures may be that it caused children who were better prepared to enter government schools (with written baseline-test status used as a coarse preparation proxy) to be more likely to leave the centers. Of course, any heterogeneity in departures could be due to a variety of other reasons, including other differences between writers and nonwriters or differential impacts of monitoring on measurement of writer versus nonwriter attendance. Duflo, Hanna, and Ryan (2012) use this same distinction to analyze heterogeneous impacts of treatment on learning outcomes and attendance. This exercise examines whether the treatment effect on recorded departure differs between writers and nonwriters, with or without a government-school marker. Thus, these results should be viewed as exploratory, and do not estimate a treatment effect of ability or of writing.

## Edit 107 at source line 20
Consistent author-name punctuation.

Before: I estimate the model for three different outcomes in Y. Departed is the departure measure used by Duflo, Hanna and Ryan (2012). Government School is an indicator equal to one if the child is classified as departed and has a government-school reason marker in at least one selected record. Residual Departure is Departed minus Government School. I conduct wild cluster bootstrap hypothesis tests that impose the null under test, use 9,999 school-level Rademacher wild-bootstrap-t draws (using a random number seed of 20260922), and account for the finite number of clusters following Cameron, Gelbach and Miller (2008). The null sets δ = 0 while leaving the treatment and writing main effects unrestricted. Table 3 reports p-values for δ, the writer-minus-nonwriter difference in treatment effects. I adjust the conventional school-clustered p-values across the three outcomes using Holm (1979), and report wild-bootstrap p-values separately. These results are exploratory as this correction does not account for the search discussed in Appendix C that considered a number of potential candidate exercises before turning to this analysis of heterogeneity.
After: I estimate the model for three different outcomes in Y. Departed is the departure measure used by Duflo, Hanna, and Ryan (2012). Government School is an indicator equal to one if the child is classified as departed and has a government-school reason marker in at least one selected record. Residual Departure is Departed minus Government School. I conduct wild cluster bootstrap hypothesis tests that impose the null under test, use 9,999 school-level Rademacher wild-bootstrap-t draws (using a random number seed of 20260922), and account for the finite number of clusters following Cameron, Gelbach and Miller (2008). The null sets δ = 0 while leaving the treatment and writing main effects unrestricted. Table 3 reports p-values for δ, the writer-minus-nonwriter difference in treatment effects. I adjust the conventional school-clustered p-values across the three outcomes using Holm (1979), and report wild-bootstrap p-values separately. These results are exploratory as this correction does not account for the search discussed in Appendix C that considered a number of potential candidate exercises before turning to this analysis of heterogeneity.

## Edit 108 at source line 20
Consistent author-name punctuation.

Before: Cameron, Gelbach and Miller
After: Cameron, Gelbach, and Miller

## Edit 109 at source line 44
Consistent author-name punctuation.

Before: Next I explore whether children’s departure from these centers may have varied by their baseline written-versus-oral test status. In the original study’s Tables 7 and 9, Duflo, Hanna and Ryan (2012) explore heterogeneity based on whether children could take a written or only an oral pretest in tables of treatment effects on presence at the center (Table 7) and treatment effects on test scores (Table 9), respectively. They do not do this heterogeneity analysis in Table 10 on leaving the center.
After: Next I explore whether children’s departure from these centers may have varied by their baseline written-versus-oral test status. In the original study’s Tables 7 and 9, Duflo, Hanna, and Ryan (2012) explore heterogeneity based on whether children could take a written or only an oral pretest in tables of treatment effects on presence at the center (Table 7) and treatment effects on test scores (Table 9), respectively. They do not do this heterogeneity analysis in Table 10 on leaving the center.

## Edit 110 at source line 47
Consistent author-name punctuation.

Before: Cameron, Gelbach and Miller
After: Cameron, Gelbach, and Miller

