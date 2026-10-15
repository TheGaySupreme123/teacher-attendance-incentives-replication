# Requirements review for the reference paper draft

This memo separates the assignment requirements from the user’s request for a full reference draft. The paper appears to be Track A (replication plus extension); Track B pre-analysis-plan rules should not be applied unless the instructor has separately approved a change of track.

## Controlling instructions and conflict resolution

The document `final_paper_instructions.txt` is the latest, specific instruction set for the final Track A paper. The earlier `seminar_instructions.txt` remains useful for the course’s general expectations, proposal/oral-defense process, and the basic replication workflow, but its older formatting and length guidance should yield to the final-paper document.

| Topic | Rule to follow for this paper | Resolution |
| --- | --- | --- |
| Track and purpose | Replicate the chosen study’s main result and make one sensible extension. | Use the Track A structure in the final-paper instructions. Do not turn the paper into a general literature review. |
| Length | Aim for 10–12 pages of main text; references and appendix do not count. | This supersedes the earlier 8–12-page aim. The final document also says the number of pages does not matter, so treat 10–12 pages as the practical target, not a reason to pad the argument. |
| Spacing and type | 12-point font, 1.5 spacing, numbered pages, numbered sections. | This supersedes the earlier 2.0-spacing/Times New Roman instruction, which appears in the older PAP writing rules and applies to Track B. |
| Cover page | No cover page. Page 1 begins with the title, author name, abstract, and relevant footnotes. | Follow the final-paper rule even if a generic seminar template suggests a cover. |
| Abstract | One paragraph, under 150 words; state the question, what was done, and what was found. | Keep this limit in both the paper and any later presentation summary. |
| Main structure | Introduction (1–2 pages), replication (2–3 pages / roughly 20–30%), extension (4–6 pages / roughly 60–70%), discussion/conclusion (about 0.5–1 page), plus AI Use Statement. | The replication should establish the benchmark; the extension carries the paper’s contribution. Weave only relevant prior work into the introduction rather than adding a standalone literature-review section. |
| Extension | One clearly motivated change to the original analysis. | Choose and defend one extension. Possible course-approved families include subgroup effects, another outcome, persistence/spillovers, a clearer uncertainty figure, or reasonable stability checks. Robustness checks belong in the appendix. |
| Tables and figures | Publication-quality, numbered, titled, discussed in the text, with 2–3 decimals, words and units on axes, and standard errors or confidence intervals. Notes must define variables, sample and N, standard-error calculation, and significance stars. | No pasted software output, pie charts, 3D/decorative graphics, or figures that do not advance the paper’s one point. |
| Citations | Use one author-date convention consistently: APA or Chicago author-date. The reference list contains only works cited. | The earlier seminar document’s Harvard suggestion is compatible in spirit, but choose APA or Chicago for this final paper and apply it consistently. |
| Replication documentation | State the exact sample, years, variable definitions, software, and missing-data treatment. Show the paper’s main result and explain whether the rerun matched it and why. | Include a shareable replication-package link where possible, plus a README with the author name, paper title, and reproduction steps. |
| AI use | Include a short, accurate AI Use Statement naming the tool, version, and dates. Keep AI conversation transcripts because the instructor may ask for them at the oral defense. | The assignment encourages AI for coding/analysis and permits copyediting but strongly discourages outsourcing writing. Because this request asks for a full AI-generated reference draft, the statement must disclose that the draft was generated with AI and must not describe the use as copyediting only. The student remains responsible for checking, revising, and defending every claim. |
| Submission | Submit a PDF by email to `pbalan@tauex.tau.ac.il` by midnight on October 15, 2026. Subject: `[Lastname] Final Paper`. File name: `Lastname_Paper.pdf`. | The final-paper date and filename supersede the earlier “date specified by the registrar” and older `Surname_final.pdf` wording. Confirm the exact surname capitalization before export. |

## What the reference draft must leave for the author to complete

The draft should contain explicit placeholders rather than inventing personal or unverifiable details:

- `[Author name]` and `[Last name]` for the title page, filename, and email subject.
- Final paper title and the chosen original article’s complete citation.
- The exact replication-package URL, access date, software/language and version, and any package or commit identifier.
- The exact sample, study years, treatment/control definitions, outcomes, covariates, missing-data rules, and analysis sample size.
- The observed replication result and the published benchmark, including any discrepancy and its documented explanation.
- The final choice and rationale for the single extension; all extension estimates, uncertainty intervals, sample sizes, and interpretation.
- The author’s own judgment about limitations and the one main point the evidence supports.
- The real AI tools, model/version names, dates, prompts or workflow details, and whether AI generated prose, analysis code, figures, or edits. Preserve the relevant transcripts.
- The shareable replication-package/README link, if created, and any data-access or licensing limits.
- The selected citation system (APA or Chicago author-date) and complete references for only cited works.

If the underlying replication has not yet been run, language such as “matches,” “does not match,” or numerical findings must remain marked as a placeholder. A reference draft must not convert an intended analysis into fabricated evidence.

## Remaining final-paper checklist

1. Confirm that the article and Track A assignment choice were approved by the instructor; the earlier seminar instructions require approval of the chosen paper.
2. Locate and preserve the original replication package. Run the original code/data, reproduce the main table or figure, and record the software, sample, years, variable definitions, missing-data handling, and exact comparison to the published result.
3. Select one extension with a clear substantive reason. Run it using a reproducible script, report uncertainty, and put additional robustness/stability checks in the appendix.
4. Rewrite and verify the reference draft in the author’s own voice. Check every number, citation, table note, figure label, and claim against the article, data, code, and output.
5. Produce clean tables and figures: numbered titles; text references; units and words on axes; sample/N and variable definitions; standard-error or confidence-interval method; significance-star explanation; no raw output, pies, 3D, or decoration.
6. Add the under-150-word abstract, numbered sections and pages, concise introduction roadmap, discussion/conclusion with limitations, AI Use Statement, references, and robustness appendix.
7. Build or link the replication package with a README containing the author name, paper title, dependencies, and reproduction instructions. Test that tables and figures regenerate from the submitted code.
8. Export and inspect the final PDF. Check 12-point type, 1.5 spacing, no cover page, title/name/abstract on page 1, page and section numbering, citation consistency, and the 10–12-page main-text target.
9. Name the file `Lastname_Paper.pdf`, email it to `pbalan@tauex.tau.ac.il` with subject `[Lastname] Final Paper` by October 15, 2026 at midnight, and retain the sent message and final PDF.
10. Prepare for the post-submission one-on-one oral defense: be able to explain the research question, original claim, replication choices, extension, evidence, limitations, and exact AI use. The earlier seminar materials also describe a proposal/progress defense; confirm separately whether that milestone was completed or remains outstanding.

## Separate presentation guidance

`presentation_guidelines.txt` is advice for slides and oral delivery, not a replacement for the final-paper rules. If slides are later made, use a clean simple design, minimal text, publication-quality copied/adapted plots and tables, no pie charts or distracting animation, and detailed practice notes. The paper itself still follows the final-paper formatting and Track A structure above.

## Relationship to the user’s request

The user asked for a full paper draft to use as a reference and for suggestions about other approaches in separate documents. That request is distinct from the instructor’s requirements. The draft can serve as a reference scaffold, but it should identify any unverified empirical values, avoid presenting placeholders as results, and include an honest AI Use Statement when adapted for submission. Alternative approaches should be kept in separate documents and treated as candidate designs until the author selects and actually runs one.
