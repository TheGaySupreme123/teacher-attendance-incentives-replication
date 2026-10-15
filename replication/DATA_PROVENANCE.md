# Data and source provenance

## Original study and public release

**Authors:** Esther Duflo, Rema Hanna, and Stephen P. Ryan.

**Article:** Duflo, E., Hanna, R., & Ryan, S. P. (2012). Incentives work: Getting teachers to come to school. *American Economic Review, 102*(4), 1241–1278. https://doi.org/10.1257/aer.102.4.1241

**Dataset:** Duflo, E., Hanna, R., & Ryan, S. P. (2019). *Replication data for: Incentives work: Getting teachers to come to school* (Version 1). American Economic Association; openICPSR project E112523V1. https://doi.org/10.3886/E112523V1

The source release was already present in the project workspace. This repository redistributes the subset required for the included attendance, transition, and archival learning analyses. The complete original release, including structural programs outside this paper's replication scope, is available through the dataset DOI.

## Source license

The original release's supplied license is preserved verbatim as [`LICENSE-original.txt`](LICENSE-original.txt). It states **copyright 2012 American Economic Association**, specifies the **Modified BSD / BSD-3-Clause license for code, scripts, programs, and software**, and **Creative Commons Attribution 4.0 International for databases, images, tables, text, and other objects**. Retain the original attribution and license when reusing the supplied materials. The original-source notice is not a claim that AEA authored or endorsed this seminar paper or its extension.

## Unchanged source and derived materials

- `data/Incentives_FINAL/Raw-Data/`: selected Stata input files, copied without changing their contents from the public release.
- `data/Incentives_FINAL/Programs/`: original Stata benchmark programs, copied without changing their contents. The paper's author did not execute these programs in Stata.
- `data/Incentives_FINAL/Output/`: selected original distributed CSV benchmark tables, copied without changing their contents.
- `scripts/`, `code/`, and `run_all.py`: Python reconstruction, verification, and exhibit-generation work prepared for Shay Ben Shabtay's replication and extension. These are additions to the original release.
- `outputs/`: derived analysis results, saved bootstrap vectors, input-hash records, and earlier exploratory learning candidates produced during this project. These files are not original-author findings merely because they use the original data.
- `results/`: reconstructed estimates, verification records, and regenerated tables and figures. Running the commands in the README replaces these generated files locally.
- `SHA256SUMS.txt`: content digests and byte counts for the public package, excluding the manifest itself.

Derived materials preserve the source attribution. Their substantive interpretation is the responsibility of this independent seminar project. The manuscript and its literature review are Shay Ben Shabtay's work with the AI assistance disclosed in the paper and repository README; the original dataset license does not identify the manuscript as an AEA publication.

## Interpretation and verification scope

The randomized intervention combined camera monitoring and attendance-linked pay. Recorded departure is constructed from the latest up to five attendance checks when schools were open. Treatment changed school opening and thus observation opportunities. Recorded departure is not verified educational dropout or a verified transfer.

The default verifier passed 12/12 checks on the recorded run. It reconstructs selected attendance and departure results and verifies the saved bootstrap vectors' p-value arithmetic. It does not rerun every original table, the structural model, every earlier learning extension, or the 9,999 bootstrap draws. See the package README for the optional transition rerun.
