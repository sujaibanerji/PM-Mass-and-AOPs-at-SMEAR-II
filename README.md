# Do the PM mass and aerosol optical properties differ between plant-material-labeled and dust-event-associated impactor filters at Hyytiälä?

Release candidate: `binder-20261020-python-only-eight-figures` — 20 October 2026.
This Python-only candidate has passed local tests and the fresh-archive default
workflow. Complete historical production validation and cloud acceptance are
pending. The repository root contains the automatic-start Binder source.

## One click, then wait

[![Launch automatic-start Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sujaibanerji/hyytiala-pm-mass-and-optical-properties/binder-20261020-python-only-eight-figures?urlpath=voila%2Frender%2FOne_click.ipynb)

The link targets the candidate tag; check the validation status below.
**Click once, then wait. The workflow starts automatically. Keep the tab open;
do not click Run, change settings, or refresh the page.** Initial environment
preparation and downloads can take several minutes. Progress and result downloads
appear on the page. Download results before leaving: Binder storage is temporary.

## What the default workflow does

- Copies the exact supplied Figure 1 artwork without redrawing or resampling it.
- Redraws Figures 2–8 from frozen processed inputs and reference tables, retaining
  the pollen grains-per-gram calculation and current layout fixes.
- Recalculates the dust-event evidence, including overlap, counts, medians and
  Cliff effects, and exports nine CSV tables.

The default uses saved uncertainty intervals; it does not recompute them.
It does not reconstruct original instrument measurements or independently
establish the original category attribution. Optional historical recomputation
is separate and preserves the existing scientific numerical calculations.
Its full production validation is still pending.

## Matching downloads and version compatibility

The matching processed data are available first through
[Zenodo DOI 10.5281/zenodo.23383412](https://doi.org/10.5281/zenodo.23383412).

| Component | Download |
| --- | --- |
| Matching data, unchanged | [data.zip from `binder-20261019-dust-evidence`](https://github.com/sujaibanerji/hyytiala-pm-mass-and-optical-properties/releases/download/binder-20261019-dust-evidence/data.zip) |
| New Python-only code | [codes.zip](https://github.com/sujaibanerji/hyytiala-pm-mass-and-optical-properties/releases/download/binder-20261020-python-only-eight-figures/codes.zip) |
| New Binder launcher/source | [binder.zip](https://github.com/sujaibanerji/hyytiala-pm-mass-and-optical-properties/releases/download/binder-20261020-python-only-eight-figures/binder.zip) |

The unchanged `data.zip` is **424,088,387 bytes**, with SHA-256
`fbcea2262e8ad179798ad7cd462031345790649b89dd0e5c7a4d75bb549dc393`.
Code and Binder downloads belong to the new tag. Their archive identities are
recorded in `VALIDATION_PYTHON_ONLY_20261020.json` and the release assets.

**Do not mix code versions.**
[Zenodo code DOI 10.5281/zenodo.23401520](https://doi.org/10.5281/zenodo.23401520)
contains the older seven-main-figure Python-only code, not this eight-figure
implementation. It is not the matching code for the current data/default workflow,
and that Zenodo code/data combination must not be described as validated together.
This GitHub release does not replace the existing Zenodo code archive.

## Validation status

A local default production run and a fresh-archive offline Binder run passed,
completing four entry points and producing all eight figures and nine matching
dust tables. All 141 applicable unit/integration tests passed with no skips.
The optional historical main-manuscript calculation finished in 1,164 seconds;
its supplementary-information calculation is still running. Complete historical
production validation and end-to-end Binder cloud acceptance remain pending.

The current release receipt is `VALIDATION_PYTHON_ONLY_20261020.json`.
Read its final results and scope before claiming acceptance. The old launcher
runtime, tests, tools, inventories, and validation receipts are preserved in
[historical/pre-python-only-launcher](historical/pre-python-only-launcher/).
The unchanged [audit](audit/) and [calibration](calibration/) directories also
retain historical evidence. These records do not validate this release.

## Size-distribution methods

The manuscript methods project remains available:

- [Copy-ready subsection](docs/methods/size-distribution/size_distribution.tex)
- [Standalone LaTeX document](docs/methods/size-distribution/main.tex)
- [Bibliography](docs/methods/size-distribution/bibliography.bib)

Keep the three files together and compile `main.tex` with pdfLaTeX and BibTeX.
When integrating the subsection into the manuscript, retain its existing
preamble and bibliography style and avoid a duplicate `sec:size` label.
