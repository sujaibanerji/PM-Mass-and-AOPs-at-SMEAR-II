# Local acceptance record — 18 October 2026

The final launcher covers **192 figures and 396 image assets**: seven current main figures, ten current supporting figures, and 175 archived historical figures with 204 companion PDF/SVG exports. All 6,210 source candidates are accounted for, with no unresolved selection decisions. The 560 pages of 21 scientific figure books are mapped to individual exports and retained figures.

## Linux execution

Validation used an isolated WSL Ubuntu environment with **Python 3.12.14**, preserving Ubuntu's system Python. All 16 scientific package versions match the original requirements exactly, and `pip check` passed. All **26 focused tests passed on Linux**, including a real symlinked virtual-environment regression, archive corruption/download failure/path escape/symlink rejection, protected destinations, reuse/tampering detection, complete gallery/export identities, escaped captions and explicit full-analysis opt-in.

The final notebook was executed in a fresh native Linux directory containing spaces. It prepared the final three archives, rendered the complete 192-figure gallery, created the 396-asset ZIP and skipped the full-analysis cell. No production job directory was created by Run All. A separate complete saved-input acceptance run took about **88 seconds**, with **293 MiB** peak child resident memory. An earlier notebook run through the Windows filesystem bridge took about 10 minutes including preparation, with about 298 MiB peak memory; those filesystem timings should not be treated as Binder timings.

The full registered Python production workflow completed with the original defaults of 5,000/2,000 draws and all requested sensitivity/size options. All five jobs passed: supporting MM, supporting SI, main figures, SI tables, and numerical reference verification. Total acceptance time, including preparation/gallery checks, was about **30.7 minutes**, with **899 MiB** peak child resident memory. The original launcher resolves Linux virtual-environment symlinks to the base interpreter; `production_entry.py` preserves the active environment for its child jobs without changing the original ZIP or scientific source. Its regression test and the full run passed.

The numerical reference check passed exact declared inventories for 175 optical/mass point rows, 150 whole-year rows, 2,000 duration/month-adjusted rows, 180 seasonal rows, 23,535 scalar collection values, 105 size point rows, 630 collection-size interval rows, 105 native-hour interval rows, 350 legacy canonical rows and 686 legacy family rows. Comparisons retain the original release's numerical tolerances and scope limits.

After the final scientific overlap cross-check, three distinct historical figures were added. The production gallery was reassembled from the already verified current outputs and the final archived bundle; no numerical calculation changed. The final 192-figure notebook and both final galleries/downloads passed their inventory, decoding, CRC and all-member checksum checks. Historical images remain archived images, not new calculations.

## Images and protected sources

Every retained raster image was inspected using contact sheets and targeted full-resolution checks. Current figure readability, paired area/volume panels, historical cohorts/backscatter/geometry labels and the browser gallery were checked. The first Linux saved-input rendering produced 17 images pixel-identical to the verified Windows production images. The final 17 production images are also pixel-identical to the verified Windows images. All 118 PDF and 86 SVG companion exports parsed successfully. Original rendering and calculation manifests remain available; portable copies accompany the result download.

All additional bundle assets were extracted and byte-compared with their original sources. Both protected original ZIP hashes remained unchanged; archive identities are recorded in `binder_release.json`. The final full-figure ZIP contains all 396 declared assets and their provenance.

The actual launcher ZIP was extracted to a fresh Linux directory containing spaces. Its notebook passed with all 192 figures and 396 assets in about 74 seconds, with the production guard disabled. A fresh `postBuild` also stopped as expected while the public URLs were unset. One independent final review found no critical or important defects. Two minor gallery issues are deferred: the production introduction retains saved-workflow wording despite correct figure-level production labels, and the extracted gallery's redundant complete-ZIP link depends on the ZIP remaining beside its directory. Individual images, companion formats and manifest links remain valid.

## Online acceptance remains outstanding

**No actual MyBinder build has been tested.** WSL tests establish local Linux execution of the commands above. They do not establish repo2docker build success, online session memory availability, launch latency or completion of the optional long calculation on MyBinder. Public publication was approved on 18 October 2026. The clean public snapshot uses version-specific GitHub release URLs. A separate actual MyBinder build and complete normal-notebook test are now being attempted; their outcome will be recorded independently.

The scientific boundary remains the original package's processed observations. Upstream instrument corrections, original category attribution, scalar physical definitions and the historical pipelines are not newly validated by this launcher. Read the inherited calculation/scope manifests.
