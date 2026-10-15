# Teacher Attendance Incentives and Recorded Student Departure

**Shay Ben Shabtay · Track A seminar paper · October 15, 2026**

[Read the final paper (PDF)](paper/BenShabtay_Paper.pdf) · [Editable paper (DOCX)](paper/BenShabtay_Paper.docx) · [Replication instructions](replication/README.md)

This repository contains the final paper and its reproducibility materials, together with an archive of the research, alternative approaches, literature review, and document development. The paper replicates selected findings from Duflo, Hanna, and Ryan (2012), then examines whether the treatment effect on recorded departure differs by children's baseline written-versus-oral test status.

## Reproduce the main results

Create a Python 3.12 virtual environment, then run from a clone or downloaded copy of this repository:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
cd replication
python3 -m pip install -r requirements.txt
python3 run_all.py
```

The default run reconstructs the attendance estimate, the Table 10 departure outcomes, and the baseline-writing interaction. It checks samples, clustered inference, saved source hashes, and the arithmetic of saved 9,999-draw wild-bootstrap p-values, then regenerates the main exhibits and Appendix A tables in `replication/results/`. The recorded verification passed **12 of 12 checks**. The software versions are pinned in `replication/requirements.txt`. Python 3.12 is recommended for installing these pinned dependencies with standard package wheels; the original recorded verification used the Python 3.13.4 environment.

The headline attendance reconstruction gives an increase in school opening of **20.7 percentage points**. In the extension, the effects on recorded departure are **26.1 points for baseline writers** and **5.0 points for nonwriters**, a **21.1-point difference**. These are exploratory subgroup findings. Recorded departure depends on checks when schools were open, which treatment itself affected; it does not establish educational dropout, a verified transfer, or a causal mechanism.

The default command verifies saved bootstrap vectors; it does not regenerate their 9,999 draws. To rerun the supplied transition audits and bootstrap procedures:

```bash
python3 run_all.py --full-analysis
```

This optional run takes longer. Neither command certifies every original-paper table, the structural model, or every earlier learning analysis. Original Stata programs are included as benchmarks and were not executed in Stata for this paper.

## What is here

| Folder | Contents |
| --- | --- |
| [`paper/`](paper/) | Final PDF and editable DOCX. These identify the final submission version. |
| [`replication/`](replication/) | Required source data, benchmark programs, Python code, saved outputs, regenerated exhibits, provenance, and file hashes. |
| [`research_archive/`](research_archive/) | Earlier research scripts, outputs, scope decisions, literature work, example drafts, alternatives, editing materials, and seminar notes. |
| [`sites/`](sites/) | Static source for the research-options and paper-comparison reading aids, with local preview instructions. |

Start with the final paper and replication package. **Archived documents and Sites preserve earlier stages of the work.** Their findings, page references, wording, and labels may have been superseded; descriptions such as “final” inside an older document do not identify the current final paper. The archive is a record of exploration, not a preregistered analysis plan or a second set of submitted findings. See [the archive guide](research_archive/ARCHIVE_README.md).

The repository includes the substantive project materials, rather than browser logs, full AI conversations, temporary files, duplicate page renders, or downloaded full-text copies of other authors' articles. The original full replication archive remains accessible through its dataset DOI.

## Sources and attribution

Duflo, E., Hanna, R., & Ryan, S. P. (2012). Incentives work: Getting teachers to come to school. *American Economic Review, 102*(4), 1241–1278. [https://doi.org/10.1257/aer.102.4.1241](https://doi.org/10.1257/aer.102.4.1241).

Duflo, E., Hanna, R., & Ryan, S. P. (2019). *Replication data for: Incentives work: Getting teachers to come to school* (Version 1). American Economic Association; openICPSR project E112523V1. [https://doi.org/10.3886/E112523V1](https://doi.org/10.3886/E112523V1).

Original-source licensing and the distinction between supplied and derived files are documented in [replication/DATA_PROVENANCE.md](replication/DATA_PROVENANCE.md), with the supplied license preserved in [replication/LICENSE-original.txt](replication/LICENSE-original.txt). This is an independent seminar project; the original authors and data distributor do not endorse its interpretations.

## AI use

During May–October 2026, I used OpenAI Codex (GPT-5.6 Sol and Luna, GPT-6 Astra and Luna, and GPT-6.1 Sol) and Claude Code (Claude Opus 4.8, Opus 5, Fable 5, Fable 5.1, and Opus 5.5) to find information, help with coding and data analysis, and provide examples of structure and wording to guide my own writing. I used the tools for copyediting and formatting, and to help prepare the tables, figures, and appendices and check their content, relevance, and presentation against the seminar requirements. Records from multiple conversations with these tools have been preserved to document this use.

The preserved conversation records are retained separately and are not published in this repository.
