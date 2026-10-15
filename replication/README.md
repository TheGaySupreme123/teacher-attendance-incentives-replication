# Teacher Attendance Incentives and Recorded Student Departure

Replication package for **Shay Ben Shabtay**, “Teacher Attendance Incentives and Recorded Student Departure.” The package contains the shareable raw inputs, source benchmark programs and shipped CSV references needed for the paper’s attendance and transition results, plus the saved transition analysis artifacts and wild-bootstrap vectors.

## Quick reproduction

Use a Python 3.12 virtual environment with the versions in `requirements.txt`, from this package directory. Python 3.12 is recommended for standard package-wheel installation; the original verification was recorded with the Python 3.13.4 environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 run_all.py
```

The quick command:

1. reconstructs the headline attendance coefficient and clustered standard error from `data/`;
2. reconstructs the raw Table 10 transition outcomes and checks the shipped child-level reference;
3. reconstructs the consensus-W interaction estimates and checks the exact sample, clustered standard errors, confidence intervals, raw p-values and Holm-adjusted p-values;
4. derives each saved wild-bootstrap p-value from its saved 9,999 t statistics and checks the reported observed statistic, seed and validation flag; and
5. writes fresh `results/verification.json`, `results/table1_replication.csv`, `results/table2_group_effects.csv`, `results/table3_interactions.csv`, `results/tableA1_sensitivity.csv`, `results/tableA2_measurement_bounds.csv`, `results/figure1.png`, and `results/figure1.svg`. The figure has the two baseline-status effects and their direct difference, with 95% cluster-robust intervals.

The quick command does not rerun the 9,999 bootstrap draws. It verifies the supplied vectors and their p-value arithmetic, which keeps the default package run bounded and reproducible. To rerun the supplied Python transition audits, including both saved-analysis replacements, use:

```bash
python3 run_all.py --full-analysis
```

That optional command can take substantially longer and writes only inside this package. The transition scripts use seed `20260922`, 9,999 repetitions, school-clustered inference, and the fixed source-data join rules documented in the scripts.

## Package contents

- `data/Incentives_FINAL/Raw-Data/` contains the attendance, roster, enrollment, baseline-writing, transition, and learning-extension Stata inputs used by the included checks.
- `data/Incentives_FINAL/Output/` contains the shipped CSV reference tables; `data/Incentives_FINAL/Programs/` contains the original Stata source benchmark programs. The `.do` files are included for provenance; the quick Python command does not require Stata.
- `scripts/` contains the original Python audit scripts and the package-local read-only verifier.
- `outputs/` contains saved audit outputs and the saved wild-bootstrap vectors used by the quick check. It also contains the saved learning-extension artifacts for the teacher-score interaction, the fixed math/language/total domain family, and the post-test distribution contrasts reported as prior candidates in Appendix C.
- `results/` contains the package-local verification record and regenerated exhibits.
- `SHA256SUMS.txt` records the SHA-256 digest and byte count for every package file except the manifest itself.

Appendix C candidates are archival in the default command: their saved outputs, frozen scope plans, raw inputs, and required scripts are included for provenance, but the 12-check quick verifier does not rerun or certify those exploratory learning analyses. To rerun them individually from this package root, use `python3 scripts/audit_learning_extension.py`, `python3 scripts/run_scope_learning_family.py`, and `python3 scripts/run_distribution_quantile_bootstrap.py`; the latter two use the saved plans under `outputs/scope_search_2026_09_22/` and can take substantially longer because they include 9,999-repetition procedures.

The transition outcome is a recorded departure from the baseline center, constructed from the latest up to five open-school attendance checks. The package includes the raw files needed for the submitted analyses rather than unrelated files from the full source archive. The research design and interpretation remain bounded by the paper’s documented measurement and treatment-dependent observation limits, and the quick verifier does not certify every original table or the archival learning extension.

## Attribution and redistribution

The supplied data and benchmark programs originate from Duflo, Hanna, and Ryan's public openICPSR release E112523V1, https://doi.org/10.3886/E112523V1, for the article https://doi.org/10.1257/aer.102.4.1241. The original AEA copyright and BSD/CC BY license are retained in [`LICENSE-original.txt`](LICENSE-original.txt). [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md) identifies unchanged supplied files and this project's derived analysis materials.

This public package is part of Shay Ben Shabtay's seminar project. The final paper is in [`../paper/BenShabtay_Paper.pdf`](../paper/BenShabtay_Paper.pdf); earlier research is separated in [`../research_archive/`](../research_archive/). The final paper and root README disclose the AI assistance used for information finding, coding and analysis, example drafts, copyediting, tables, figures, appendices, and requirements checks. Full conversation records are retained separately.
