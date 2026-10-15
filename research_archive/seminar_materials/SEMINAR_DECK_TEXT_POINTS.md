# Track A Seminar Deck Text Points

## Slide 1 - Track A Project

### Title

Track A: Replicating Duflo, Hanna, and Ryan (2012)

### Main bullets

- Paper: "Incentives Work: Getting Teachers to Come to School."
- Track A task: reproduce the main result, then continue with one focused follow-up.
- Original paper question: can monitoring plus attendance-based pay reduce teacher absence?
- My follow-up question: are lower-baseline-score teachers affected more positively than higher-baseline-score teachers?

### Graphic

- Three-step Track A progress bar:
  - Step 1: original experiment;
  - Step 2: replication of main attendance result;
  - Step 3: follow-up on lower-baseline-score teachers.
- Large callout:
  - "Main original result: +21 pp school-open rate."

## Slide 2 - Original Paper Question

### Title

Original Question: Can Incentives Fix Teacher Absence?

### Main bullets

- Governance problem:
  - schools may exist, but learning fails if teachers do not show up.
- Setting:
  - Seva Mandir nonformal education centers in rural Rajasthan, India.
- Population:
  - single-teacher schools serving children outside the regular public system.
- Core question:
  - can direct monitoring and financial incentives increase teacher attendance?
- Why it matters:
  - attendance is a basic service-delivery failure and a precondition for learning.

### Graphic

- Simple problem chain:
  - teacher absence -> less instruction time -> weaker learning outcomes.
- Add a question mark above the intervention:
  - "Can monitoring + pay incentives break this chain?"

## Slide 3 - Original Treatment Design

### Title

Original Treatment: Cameras + Attendance Pay

### Main bullets

- Treatment schools:
  - date-stamped camera photos at opening and closing;
  - valid school day required enough time between photos and enough children present;
  - teacher pay increased with valid attendance days.
- Control schools:
  - fixed monthly pay;
  - ordinary monitoring.
- Important wording:
  - the randomized treatment is bundled;
  - it is not camera-only and not pay-only.

### Graphic

- Treatment-control comparison diagram:
  - Control: fixed pay + ordinary monitoring.
  - Treatment: camera evidence + attendance-linked pay.
  - Outcome measured for both: school open during unannounced random check.

## Slide 4 - What The Original Paper Found

### Title

Original Findings

### Main bullets

- Attendance result:
  - treatment schools were open about 79% of the time;
  - control schools were open about 58% of the time;
  - difference: about +21 percentage points.
- Persistence:
  - effects remain positive before mid-test, between mid-test and post-test, and after post-test.
- Learning result:
  - student test scores rose by about 0.17 standard deviations.
- Heterogeneity clue:
  - the paper reports a larger attendance effect for below-median baseline teacher-score schools.

### Graphic

- Main visual should show the original findings, not the follow-up:
  - side-by-side bars for control open rate 0.58 and treatment open rate 0.79;
  - arrow or label: "+0.21".
- Small secondary callouts:
  - "+0.17 SD student test scores";
  - "larger effect below median teacher score."

## Slide 5 - What I Recreated So Far

### Title

Replication Work So Far

### Main bullets

- Replication target:
  - Table 2 attendance effect.
- Outcome:
  - school open during an unannounced random check.
- Estimation:
  - `open = alpha + beta * treatment + error`;
  - standard errors clustered by school.
- Data work:
  - used the replication package;
  - inspected original Stata code and output files;
  - recreated the key cleaning logic in Python because the old Stata paths are not plug-and-play locally.
- Agentic AI disclosure:
  - used Codex, Claude Code, and Claude Design to help inspect files, organize evidence, draft code/text, and refine the presentation;
  - final interpretation and validation remain my responsibility.
- Original package benchmark:
  - all post-baseline effect: +0.21, SE 0.03;
  - period effects: +0.20, +0.17, +0.23.

### Graphic

- Replication evidence table:
  - rows: all post-baseline, until mid-test, mid-test to post-test, after post-test;
  - columns: original package estimate, current replication target/status.
- Use the original values from:
  - `data/Incentives_FINAL/Output/table2.csv`.

## Slide 6 - My Follow-Up Question

### Title

Follow-Up: Do Lower-Score Teachers Respond More?

### Main bullets

- Starting point from the origincal paper:
  - below-median teacher-score schools show a larger attendance effect.
- My continuation:
  - use the same experiment and data to examine that pattern more directly.
- Main question:
  - are initially lower-baseline-score teachers affected more positively than higher-baseline-score teachers?
- Why this is interesting:
  - if weaker-baseline teachers respond more, the program may reduce attendance gaps;
  - if only stronger teachers respond, the policy interpretation is different.
- Careful wording:
  - "lower baseline teacher score" is the measured variable;
  - it should not be overread as a complete measure of teacher quality.

### Graphic

- Research-question funnel:
  - original average effect -> original teacher-score heterogeneity -> my focused follow-up.
- Put the exact follow-up question in the center:
  - "Does the treatment help lower-baseline-score teachers more?"

## Slide 7 - Preliminary Results And Validation Still Needed

### Title

What I Found Thus Far

### Main bullets

- Preliminary teacher-score split:
  - high-score treatment effect: about +14.5 pp;
  - low-score treatment effect: about +24.4 pp;
  - low-minus-high difference: about +9.8 pp, p about 0.105.
- Preliminary gap pattern:
  - control schools show about a 10.0 pp high-minus-low attendance gap;
  - treatment schools show almost no high-minus-low attendance gap.
- Interpretation so far:
  - evidence points toward lower-score teachers catching up in attendance;
  - this continues the original paper's heterogeneity finding rather than creating a new treatment arm.
- Still to validate:
  - rerun and document the replication end to end;
  - test robustness to score definition, fixed effects, and period splits;
  - keep the claim exploratory until validation is complete.

### Graphic

- Use one main preliminary figure:
  - `outputs/teacher_score_extension/teacher_score_catchup_open_rates.png`
- Optional second figure if there is space:
  - `outputs/teacher_score_extension/teacher_score_attendance_gradient.png`
- Add a small label on the slide:
  - "Preliminary - still validating."

## Optional Backup Slide - Current Work Plan

### Title

Next Steps Before Final Paper

### Main bullets

- Finish clean replication table for Table 2.
- Verify all Python outputs against original Stata output files.
- Decide whether the final follow-up analysis is:
  - median split;
  - continuous score gradient;
  - or both, with clear caution.
- Add robustness checks:
  - period fixed effects;
  - block fixed effects;
  - score quartiles;
  - sensitivity to teacher-score definition.
- Write final claim conservatively:
  - treatment appears to raise attendance more among lower-baseline-score teachers, but this is exploratory heterogeneity.

### Graphic

- Checklist graphic:
  - replication;
  - teacher-score analysis;
  - robustness;
  - final paper.
