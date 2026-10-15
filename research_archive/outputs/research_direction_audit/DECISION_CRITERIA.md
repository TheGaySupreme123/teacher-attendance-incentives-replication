# Research-direction audit: decision criteria

Date: 2026-09-22. Scope: choose an extension of Duflo, Hanna, and Ryan (2012), not write the seminar paper.

## User's stricter criteria

1. Use only measurements already present in the original replication package. No new respondents, external explanatory datasets, invented values or simulated substantive findings.
2. Add a substantive question or refinement that is not already answered or explicitly explained in the original article, footnotes, appendix, or supplemental analyses.
3. Keep the analysis feasible for a seminar project. A complete structural re-estimation is not the default.
4. Choose a question for its scientific value, feasibility and identification, not because a searched specification has a small p-value.

## Candidate set fixed for this review

- Learning: treatment effect on post-test TOTAL achievement moderated by continuous BASELINE TEACHER score. Midline total score is secondary. No selecting mathematics/language because one is significant.
- Progression: treatment effect on government-school transition moderated by BASELINE CHILD writing status. Dropout excluding transfers is a distinct secondary outcome. Do not promote a prior exploratory dropout interaction solely because it looked significant.
- Attendance-score catch-up: reject as new substantive headline if the original already states it. Formal interaction and sensitivity analyses can be support, not a substitute for substantive novelty.
- Generic attendance robustness: evaluate as supporting checks, not the preferred main contribution under the current brief.

## Required evidence before recommending a direction

- Audit the whole article and available journal supplement, including related explanations, tables and footnotes. Record what was read, what overlaps and what is unavailable. Absence is a bounded search conclusion, not universal proof of originality.
- Reconstruct the relevant original table from raw inputs. Retain sample sizes, estimates, standard errors, variable/scale definitions, joins, exclusions and deviations.
- Define the added statistical contrast explicitly. A treatment-by-baseline-score interaction is different from including score as a control, but does not identify the causal effect of teacher skill itself.
- Report confidence intervals, number of schools, plausible sensitivity and missing-outcome risks. No conclusions from significance in one group versus nonsignificance in another.
- Keep the full bundled intervention as the treatment. Do not claim attendance mediates learning causally from a simple subgroup analysis.

## Prior exploration and inference

Prior work has inspected teacher-score interactions and a research subagent ran preliminary student-outcome screens. This review is exploratory, not preregistered or independent confirmation. Candidate selection and any subsequent paper must disclose that history. Analytical decisions can be fixed for future work, but cannot retroactively make already inspected data confirmatory.

## Artifacts and ownership

- Original-overlap audit: original_overlap_audit.md.
- Learning reconstruction/audit: scripts/audit_learning_extension.py and learning_* outputs.
- Transition reconstruction/audit: scripts/audit_transition_extension.py and transition_* outputs.
- Root review integrates these into the existing decision site while retaining raw input files unchanged.
