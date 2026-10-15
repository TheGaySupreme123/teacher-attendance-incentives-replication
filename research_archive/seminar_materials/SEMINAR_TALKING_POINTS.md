# Seminar Talking Points: Track A Replication + Follow-Up on Duflo, Hanna, and Ryan (2012)

## One-Minute Version

- My Track A paper is Duflo, Hanna, and Ryan (2012), "Incentives Work: Getting Teachers to Come to School."
- The original paper studies whether better monitoring plus financial incentives can reduce teacher absenteeism in rural India.
- The experiment was run with Seva Mandir nonformal education centers in Rajasthan.
- The treatment was not just "give cameras" and not just "pay bonuses." It bundled two things:
  - daily camera monitoring of teacher attendance, using tamper-proof date and time stamps;
  - an attendance-linked salary rule, where teachers earned more when they had more valid school days.
- The original headline result is that treatment schools were open about 21 percentage points more often than control schools.
- The original paper also reports that children in treatment schools scored about 0.17 standard deviations higher after one year.
- My replication focus is the cleanest main result: Table 2, Panel A, the effect on whether the school was open during unannounced random checks.
- My follow-up continues the original paper's own heterogeneity result: it asks whether lower-baseline-score teachers are affected more positively than higher-baseline-score teachers.
- The strongest current follow-up result is a preliminary gap-closing interpretation:
  - in control schools, higher baseline teacher score predicts higher attendance;
  - under treatment, that score-attendance gradient nearly disappears;
  - low-score treated teachers catch up to high-score treated teachers in attendance.

## Assignment Fit

- The seminar instructions define Track A as replication plus extension.
- Track A asks me to:
  - obtain a public replication package;
  - reproduce the main result;
  - explain whether the replication matches the published paper;
  - make one sensible extension;
  - explain what I did, why I did it, and how AI/code was used.
- Duflo, Hanna, and Ryan (2012) is explicitly listed in the seminar instructions as a recommended Track A option.
- It is a good fit because:
  - the paper has one clear headline number: roughly a 21 percentage point increase in teacher attendance;
  - the replication package is available through openICPSR and is already downloaded locally;
  - the original data include both attendance outcomes and baseline teacher scores, which allows a meaningful follow-up without changing the experimental design;
  - the topic is directly connected to governance: how to make public-service delivery work when monitoring and incentives are weak.

## What The Original Paper Does

- Research question:
  - Can monitoring plus financial incentives reduce teacher absenteeism and improve student learning?
- Setting:
  - rural Rajasthan, India;
  - single-teacher nonformal education centers operated by Seva Mandir;
  - high teacher absenteeism at baseline.
- Unit of intervention:
  - the school/teacher, because each nonformal education center typically has one teacher.
- Treatment group:
  - teachers received a camera;
  - students photographed the teacher and class at the start and end of the school day;
  - valid school days required both opening and closing photos, separated by enough time and showing enough children;
  - salary depended on valid attendance days.
- Control group:
  - teachers continued with fixed monthly pay and ordinary monitoring.
- Outcomes:
  - school open during unannounced random checks;
  - teacher attendance from camera records in treated schools;
  - student attendance and instruction time;
  - student test scores and movement into formal schools.
- Main published findings:
  - treatment schools were open much more often than control schools;
  - the original Table 2 output reports a treatment effect of 0.21 with clustered standard error 0.03;
  - effects persisted before the mid-test, between the mid-test and post-test, and after the post-test;
  - students in treatment schools received more instruction time;
  - student test scores increased by about 0.17 standard deviations;
  - the paper reports no clear evidence that teachers compensated by reducing classroom effort when present.

## What I Am Recreating

- The core replication target is Table 2, especially the main attendance effect:
  - dependent variable: `open`, whether the school was open during an unannounced random check;
  - independent variable: `treat`, assignment to the camera-plus-incentive program;
  - standard errors clustered by school;
  - baseline month excluded;
  - closed schools dropped according to the original Stata code.
- Why Table 2 is the right replication anchor:
  - it is the simplest and clearest causal result in the paper;
  - it uses the random assignment directly;
  - it is easy to explain in a short seminar presentation;
  - it gives me a stable base before continuing into heterogeneity analysis.
- Reproduction path:
  - the replication package has original Stata code and original Stata-style CSV/log outputs;
  - because the original code has old Windows paths and Stata is not available in this shell, the practical approach is Python reimplementation from the raw `.dta` files;
  - the current repo has scripts that load the same raw Stata data and reproduce the relevant cleaning logic;
  - the original package output `data/Incentives_FINAL/Output/table2.csv` reports 0.21, 0.20, 0.17, and 0.23 across all post-baseline, until mid-test, mid-to-post, and after-post periods.
- Current status:
  - initial project snapshot committed the replication package, original outputs, exploratory notes, scripts, and generated figures;
  - the second commit clarified that the experimental treatment is bundled camera monitoring plus pay incentives, and added the gap-closing analysis;
  - the latest commit added an HTML dashboard and QA screenshots for the teacher-score follow-up.

## What I Am Continuing From The Original Paper

- The original paper already shows that the treatment worked on average.
- It also reports heterogeneity by above- and below-median teacher baseline test score:
  - above-median teacher-score effect: about 0.15;
  - below-median teacher-score effect: about 0.24.
- My follow-up continues from that finding and tries to interpret it more carefully.
- Instead of only saying "low-score teachers respond more," the follow-up asks:
  - Are low-score teachers uniquely affected?
  - Or is the larger low-score effect mainly a gap-closing pattern because low-score control schools start with lower attendance?
- The current evidence favors the gap-closing story:
  - both high-score and low-score teachers respond positively;
  - the low-score point estimate is larger;
  - the binary low-minus-high interaction is suggestive, with p about 0.105, so it should not be overclaimed as a sharp subgroup proof;
  - the control high-minus-low attendance gap is about 10.0 percentage points;
  - the treatment high-minus-low attendance gap is about 0.2 percentage points;
  - that implies about 98 percent of the control gap is closed descriptively.
- The continuous gradient result is the cleanest current follow-up result:
  - in control schools, each one-standard-deviation increase in baseline teacher score predicts about 8.4 percentage points higher attendance;
  - the treatment-by-score interaction is about -6.9 percentage points;
  - under treatment, the implied score-attendance slope is only about 1.5 percentage points and is not statistically distinguishable from zero.
- The follow-up also checks timing and quartiles:
  - the low-score difference is largest after the post-test;
  - the first three score quartiles all show large positive effects;
  - the top quartile has the smallest treatment effect estimate;
  - this supports a gradient-flattening story more than a strict median-cutoff story.

## Why This Follow-Up Matters

- It is not just a cosmetic chart.
- It changes the interpretation of who benefits from the intervention.
- Average treatment effect:
  - tells me whether the program works overall.
- Gap-closing analysis:
  - asks whether the program especially helps schools where baseline teacher capacity or preparation is weaker.
- Policy interpretation:
  - if monitoring plus incentives only helped already stronger teachers, the equity story would be weaker;
  - if it helps lower-score teachers catch up in attendance, the intervention may reduce an attendance inequality inside the system.
- Governance interpretation:
  - the treatment may substitute for weak internal motivation, weak supervision, or low baseline professional capacity;
  - it appears to weaken the relationship between baseline teacher score and absenteeism.
- Presentation-safe contribution:
  - "I replicate the headline attendance effect and continue the paper's teacher-score finding by testing whether the bundled monitoring-plus-incentive treatment appears to help lower-baseline-score teachers catch up in attendance."

## Treatment Language To Use Carefully

- Correct:
  - "bundled camera-monitoring plus attendance-pay treatment";
  - "treatment assignment";
  - "monitoring and incentives together";
  - "reduced-form effect of the full program."
- Avoid:
  - "camera-only treatment";
  - "incentive-only treatment";
  - "I separately estimate the effect of monitoring and the effect of pay";
  - "my treatment arms."
- Why:
  - the randomized design has one main treatment contrast: schools assigned to both camera monitoring and attendance-linked pay versus schools with fixed pay and ordinary monitoring;
  - the original paper uses a structural model and additional data to study financial-incentive mechanisms, but the simple randomized attendance regression does not separately identify monitoring-only and pay-only effects.

## AI Use Disclosure To Include On Slide 5

- Short slide wording:
  - "Agentic AI used: Codex, Claude Code, and Claude Design for file inspection, evidence organization, code/text drafting, and presentation refinement. Final interpretation and validation are my responsibility."
- Slightly longer oral wording:
  - "I used agentic AI tools, specifically Codex, Claude Code, and Claude Design, to help inspect the replication package, organize the source material, draft code and text, and refine the presentation. I remain responsible for the final interpretation, validation, and claims."

## What I Learned Thus Far

- The paper is feasible for Track A because the replication package is present locally and the original outputs are readable.
- The main result is simple enough to explain:
  - treatment increases the probability that a school is open by about 21 percentage points.
- The old replication package is not plug-and-play:
  - original Stata scripts use old Windows-style paths;
  - local work therefore recreates the logic in Python.
- The original result is not fragile in the original output:
  - Table 2 shows positive effects in every period: all post-baseline, until mid-test, mid-to-post, and after-post.
- Randomization-balance checks do not support a "randomization failed" follow-up:
  - checked standardized differences are modest after cleaning sentinel values;
  - this should be a validation check, not the main claim.
- The stronger follow-up direction is teacher-score gap closing:
  - control schools show a meaningful attendance gap by baseline teacher score;
  - treatment schools do not;
  - the score-attendance gradient is flattened under treatment.
- Exploratory camera-behavior clustering is interesting but should remain secondary:
  - treated schools can be described as high-attendance, middle/threshold-sensitive, and low/variable response profiles;
  - because those profiles use post-treatment treated-school behavior, they are descriptive mechanism evidence, not causal treatment-effect evidence.

## Main Numbers To Say Out Loud

- Original headline attendance effect:
  - "Treatment schools were open about 21 percentage points more often than control schools."
- Original learning result:
  - "Children's test scores increased by about 0.17 standard deviations."
- Replication table anchor:
  - "The original package output reports 0.21 with clustered standard error 0.03 for all post-baseline random checks."
- Teacher-score split:
  - "High-score teacher schools: about +14.5 percentage points."
  - "Low-score teacher schools: about +24.4 percentage points."
  - "The difference is about 9.8 percentage points, but the p-value is about 0.105, so I treat it as suggestive."
- Gap closing:
  - "In control schools, high-score teachers have about a 10 percentage point attendance advantage."
  - "In treatment schools, that gap is almost zero."
- Continuous gradient:
  - "In control schools, a one-standard-deviation higher teacher score predicts about 8.4 percentage points higher attendance."
  - "Under treatment, the implied slope is about 1.5 percentage points and not statistically significant."

## How To Frame The Seminar Argument

- Start with the governance problem:
  - education access improved, but learning depends on teachers actually being present;
  - absenteeism is a service-delivery failure.
- Then explain the experiment:
  - the program combined better monitoring with a clear pay rule;
  - random assignment makes the treatment-control comparison credible.
- Then explain the replication:
  - I focus on the main attendance result;
  - I reproduce the original cleaning logic and regression logic using the replication data;
  - the result matches the original package output.
- Then explain the follow-up:
  - the original paper reports stronger effects among lower-score teachers;
  - I continue from that result and ask whether lower-baseline-score teachers are affected more positively than higher-baseline-score teachers;
  - I ask whether that is better understood as response heterogeneity or as gap closing;
  - the evidence supports the gap-closing interpretation.
- End with the limitation:
  - the treatment is bundled, so the follow-up does not say whether cameras or pay incentives are more important;
  - the teacher-score analysis is exploratory heterogeneity, so it should be framed as evidence and interpretation, not a separate randomized design.

## Deck Speaker Notes

- Slide 1:
  - "This is a Track A project. The goal is not to invent a new experiment, but to replicate a published experiment and then continue it with one focused follow-up."
  - "The original paper asks whether monitoring and attendance-based pay can reduce teacher absence. My follow-up asks whether the effect is stronger for teachers with lower baseline scores."
- Slide 2:
  - "The governance problem is simple: schools can exist on paper, but if teachers are absent, children lose instruction time."
  - "This is why teacher attendance is a meaningful outcome for a governance-through-experiments seminar."
- Slide 3:
  - "The treatment should be described carefully. The randomized treatment bundles cameras and attendance-linked pay. I am not separately identifying camera-only or pay-only effects."
- Slide 4:
  - "The original paper's main finding is the 21 percentage point attendance increase. It also finds higher student test scores and reports stronger attendance effects for below-median teacher-score schools."
  - "That last finding is the bridge to my follow-up."
- Slide 5:
  - "My replication target is Table 2 because it is the cleanest headline result. The replication package gives the benchmark numbers, and the local work recreates the logic in Python."
- Slide 6:
  - "I am not adding an unrelated topic. I am continuing a pattern the original paper already found: lower-baseline-score teachers seem to have a larger treatment effect."
  - "I will use the phrase lower baseline teacher score, not simply bad teachers, because the score is a measured proxy and not the whole definition of teacher quality."
- Slide 7:
  - "The current results are preliminary. The low-score effect is larger in point estimate, and the gap-closing pattern is interesting, but I still need to validate robustness before making it the final paper claim."
  - "The safe current claim is: evidence so far suggests the treatment may help lower-baseline-score teachers catch up in attendance."

## Likely Questions And Good Answers

- Question: What exactly is the treatment?
  - Answer: Assignment to a package combining daily camera monitoring and attendance-linked pay. Teachers in treatment schools had date-stamped photos taken at the start and end of the day, and salaries depended on valid attendance days. Control teachers stayed under fixed pay and normal monitoring.
- Question: Are you testing cameras versus incentives?
  - Answer: No. The reduced-form experiment identifies the bundled program effect. The original paper uses structural modeling to learn more about incentives, but my replication and follow-up use the randomized treatment indicator.
- Question: What is your replication?
  - Answer: I replicate the Table 2 attendance effect: regress whether a school was open during unannounced random checks on treatment assignment, excluding the baseline month and clustering standard errors by school.
- Question: What is your follow-up beyond replication?
  - Answer: I continue the original teacher-score heterogeneity result and test whether it looks like gap closing. In control schools, lower teacher-score schools attend less. Under treatment, low-score and high-score teachers attend at almost the same rate.
- Question: Is the low-score effect significantly larger?
  - Answer: The low-score point estimate is larger, but the binary interaction is only suggestive. That is why I emphasize the gap-closing decomposition and the continuous score gradient rather than making a strong claim from one median split.
- Question: Could the teacher-score result be random imbalance?
  - Answer: The balance check does not suggest that treatment schools were stacked with lower-score teachers. If anything, treatment schools look slightly stronger on baseline teacher score, so that does not mechanically explain the low-score catch-up pattern.
- Question: Are conditional classroom outcomes causal?
  - Answer: No. Outcomes conditional on the school being open are descriptive because treatment changes whether the school is open. They are useful only as a check that attendance gains do not obviously come with visible classroom collapse.
- Question: What is the main limitation?
  - Answer: The treatment is bundled, and the follow-up is exploratory heterogeneity. It strengthens interpretation of the treatment effect but does not create new random treatment arms.

## Sources And Local Evidence

- Original paper PDF: `/Users/shayb/Downloads/Duflo-IncentivesWorkGetting-2012.pdf`
- Seminar instructions PDF: `/Users/shayb/Downloads/Experiments Seminar Paper Instructions 2026.pdf`
- Original Table 2 package output: `data/Incentives_FINAL/Output/table2.csv`
- Main work plan: `TRACK_A_DUFLO_WORK_PLAN.md`
- Extension memo: `TEACHER_SCORE_EXTENSION_MEMO.md`
- Exploratory notes: `EXPLORATORY_EXTENSION_NOTES.md`
- Teacher-score extension script: `scripts/teacher_score_extension.py`
- Teacher-score extension outputs: `outputs/teacher_score_extension/`
- Exploratory outputs: `outputs/exploratory/`
