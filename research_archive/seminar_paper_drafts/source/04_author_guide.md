# Guide to Revising and Defending the Seminar Paper

## 1 What the document set contains

The main paper is a full English reference draft of a Track A replication and extension of Duflo, Hanna, and Ryan's teacher-attendance experiment. Its chosen question is whether treatment changes recorded departure from the original nonformal school differently by baseline written-test status. It contains a complete argument, verified numerical exhibits, references, an AI Use Statement, and appendices. It is a model for developing your own paper. The author name, precise AI model history, individual contribution statement, and shareable replication-package link remain to be completed.

The two alternative memos describe other substantive routes using the same data. The teacher-score memo examines whether the program's learning response differs with a teacher's baseline test score and whether mathematics and language differ. The distribution memo examines the lower quartile, median, upper quartile, and spread of observed learning. Both contain exact current results, a method, a feasible plan, and a full-paper outline. They are separate research choices, not additional main sections to paste into the departure paper.

## 2 Choosing among the approaches

| Approach | Main question | Current evidence | Practical assessment |
|---|---|---|---|
| Recorded school departure | Does the departure response differ by baseline written-test status | Interaction 21.1 percentage points with 95 percent CI 6.9 to 35.3 | Strongest current statistical signal and moderate work but substantial measurement limits |
| Learning distribution | Does the observed post-test distribution shift at its lower tail or change spread | Lower-quartile difference 0.081 SD with 95 percent CI -0.081 to 0.219 | Clear new estimand within audited original materials but inconclusive evidence |
| Learning by teacher score | Does baseline teacher score moderate learning effects | Total-score interaction 0.132 SD with 95 percent CI -0.009 to 0.273 | Substantive and feasible but inconclusive and weaker with geographic controls |

Choose the departure route if you want to build on the strongest existing statistical contrast and can explain the operational outcome honestly. Choose a learning route if the learning question interests you more and you are comfortable making uncertainty the conclusion. A two-sided p-value above .05 does not disqualify a research question. It does prevent a claim that the present data establish that particular effect at the conventional threshold. None of the routes should be redesigned merely to cross that threshold.

A measurement-focused treatment of departure is a possible variation within the chosen route: ask how far the writing-status interaction survives documented attendance-code and observation-history ambiguity. The existing bounds make that feasible. It would change the emphasis toward measurement rather than educational behavior. It should not claim that the algebraic ranges solve the treatment-dependent observation problem or constitute independent confirmation. Routine teacher-score attendance catch-up and outage-persistence analyses are weaker main contributions under your strict originality rule because the original paper already discusses closely related patterns.

## 3 How the attached instructions were applied

The newer Final Paper Instructions control the reference draft where they differ from the earlier seminar document. The draft follows Track A rather than the Track B pre-analysis-plan template. It uses an abstract under 150 words, numbered sections, numbered pages, 12-point body type, 1.5 spacing, no separate cover page, Chicago author-date references, and numbered tables and figures. The paper has one main extension, no standalone literature-review section, and robustness checks in an appendix. References and appendices sit outside the target main-paper length.

The earlier seminar document gives an eight-to-twelve-page aim for Track A and specifies double spacing and a ten-page maximum in its PAP writing rules. The newer final instructions specify 1.5 spacing and a Track A target of ten to twelve pages. The draft uses those newer instructions. Likewise, the newer final instructions specify Lastname_Paper.pdf. They give October 15, 2026, by midnight as the deadline, with an email subject of [Lastname] Final Paper. Those are requirements recorded in the supplied document, not confirmation that a submission or instructor approval has occurred. This task has not sent an email or submitted any file.

The presentation guide and newer final instructions prohibit pie charts. The paper therefore uses a coefficient plot with intervals, even though the earlier research-options website contains pies for explanation. Every exhibit defines the sample, units, outcome, and uncertainty method. This reference package does not create a new presentation, and slide-only suggestions were not treated as instructions to do so.

## 4 Revise the paper in your own voice

The final instructions allow AI-assisted coding and require an AI Use Statement. They strongly discourage outsourcing writing. Your request here was explicitly for a full reference draft, so the document honestly discloses substantive AI drafting. It does not describe this work as copyediting. Use the draft to understand the argument and then revise the prose, interpretations, and emphasis yourself. Keep this conversation and the September 22 research conversation for the oral defense.

Replace the author field with the correct name. Rewrite the introduction around the reason the question matters to you. Check each empirical sentence against its named table or source file. Keep the operational endpoint and exploratory qualification in the abstract and introduction, where a reader can see them immediately. Do not replace recorded departure with educational dropout, or baseline written-test status with a claim of precisely measured literacy.

The current disclosure identifies Codex for the October 7 draft. It leaves the precise model variants to be verified from the current and September workflow records. Complete that information from the retained transcripts and account history. Record any analysis you rerun yourself and any decisions you make. Only then change statements about your personal contribution. The course also requires instructor approval of the original article choice; the supplied conversation confirms your selection, not the instructor's approval. Verify that status in your own records before submission.

## 5 Reproduce and inspect the evidence

The accompanying build_documents.py reads the stored CSV and JSON analyses and creates the formatted documents and exhibits. The verify_results.py script recomputes the main attendance coefficient, reconstructs the departure cohort, checks the interaction and four cell counts, and validates the saved bootstrap p-value and input hashes. Run it from the workspace with the documented analysis Python environment. It writes a separate verification record under this draft folder and does not replace the original analysis outputs.

The current main departure analysis contains 2,195 unique child identifiers in 111 schools. The two alternative learning samples contain source rows with repeated school-child keys. Their memos state both counts. This is why sample numbers cannot be copied from one approach into another. The original attendance replication is a different unit again: 3,071 school visits in 113 schools. Be able to explain all three distinctions.

For submission, prepare a reproducible package with the original data where licensing permits or documented access instructions, the analysis scripts, a pinned computational environment, exhibit sources, and a README. Follow the data package's license when sharing it. The course encourages a shareable folder URL. No such folder has been published by this task. A local reproducibility record is supplied; public accessibility and a clean-environment rerun remain separate tasks.

## 6 Prepare for the oral defense

Be ready to explain the experiment's unit of randomization, why uncertainty is clustered by school, and why the intervention is a bundle. State the departure rule in one sentence: zero recorded attendance in the last available up-to-five open-school checks. Explain why that rule depends on a program outcome, school opening. Then show the main arithmetic: the writer effect of 26.1 points minus the nonwriter effect of 5.0 points equals a 21.1-point interaction.

Explain why the result requires a direct interaction test. A significant writer effect and an insignificant nonwriter effect do not alone establish a significant difference. Explain why the incomplete-history and coding bounds have no p-values: they vary unknown outcomes over allowable values rather than estimating sampling uncertainty. Explain why the exclusion check changes the sample and why the government-school marker cannot identify every child's destination.

Finally, give a transparent account of how the question was selected. The project inspected several possible extensions before choosing departure. The three-outcome Holm correction covers only that fixed family. The narrow contribution is a previously unreported comparison in the audited original materials, supported by exploratory evidence. The strongest defense is a precise account of what the data show and where their interpretation ends.

## 7 Final review before submission

1. Complete the author name, exact AI history, human contribution details, and instructor-approval status.
2. Rerun the verification and chosen analysis in the recorded environment and inspect every exhibit.
3. Rewrite the reference prose in your own voice and check that every claim remains supported.
4. Read the final PDF for page breaks, numbering, equation rendering, captions, and references.
5. Add the shareable replication-package URL and confirm its access and README.
6. Use the instructor's required filename and email subject, and retain the submitted PDF and confirmation.

This document set makes the proposed paper concrete. The remaining work is author revision, ownership, reproducibility packaging, and submission, not another search for a favorable p-value.
