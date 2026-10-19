# Hyytiälä manuscript analysis and figures

This Python code accompanies the manuscript and its supplementary information. The current gallery contains **131 distinct scientific figures and 282 image assets**: eight main-manuscript figures, ten current supporting figures and 113 archived historical figures.

[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://gesis.mybinder.org/v2/gh/sujaibanerji/hyytiala-binder-reviewer/fd08ceca941a26e49c6599491babe70d1a3e934f?urlpath=voila/render/One_click.ipynb)

**[Open Binder](https://gesis.mybinder.org/v2/gh/sujaibanerji/hyytiala-binder-reviewer/fd08ceca941a26e49c6599491babe70d1a3e934f?urlpath=voila/render/One_click.ipynb)**, then click **Run full analysis**. Progress, the gallery and downloads appear on the same page. Reviewers do not need an account or notebook editing.

Estimated calculation time is **10–30 minutes**, depending on the Binder server, with about five minutes for initial startup. Calculation runs on Binder's servers; internet speed mainly affects page loading and downloads. These are estimates, not guarantees. Download results before leaving because Binder storage is temporary.

## Calibration verification and Zenodo identifiers

The author supplied separate archival identifiers: [data, 10.5281/zenodo.23383412](https://doi.org/10.5281/zenodo.23383412) and [code, 10.5281/zenodo.23401520](https://doi.org/10.5281/zenodo.23401520). They did not yet resolve publicly during the 19 October 2026 check and may be reserved draft identifiers.

An independent check reproduces Figure S9 of [Banerji et al. (2025)](https://acp.copernicus.org/articles/25/16895/2025/acp-25-16895-2025-supplement.pdf) by OLS with an intercept on **37,020 paired hourly medians**: **AE33_660 = 2.33 × MAAP_637 + 0.16; R² = 0.96**. The original authored recipe uses equal-value runs of at least 10 records and strict two-sided ratios below 10. The historical mean-named plotting block reused the median inputs.

The current inverse **(AE33 − 0.16) / 2.33** is already correct. An arithmetic audit of **204,908 inlet-hours**, all seven absorption channels in both inlets, STP scaling, hourly quality screening and the portable input passed. The existing calibrated optical values remain unchanged; the current presentation revision adds the pollen ratio calculation. This reproduction checks the historical 660–637 nm fit; it does not independently calibrate every wavelength.

The clean reproducer, fit, source hashes and audit are in [calibration/README.txt](https://github.com/sujaibanerji/hyytiala-binder-reviewer/blob/main/calibration/README.txt). The additional S9 plot is separate from the 131-figure production gallery. Current manuscript/SI reading copies are supplied in the author's `manuscripts.zip`; reference manuscript copies inside `data.zip` remain the frozen inputs for the earlier renderer checks. The final local Zenodo preparation uses separate code/data records and includes this verification supplement.

## Current version

`binder-20261019-pollen` adds the current main-manuscript pollen grains-per-gram Figure 6 and full-precision CSV. It generates eight main figures, ten current supporting figures and 113 archived figures. Size distributions and uncertainty are now Figures 7 and 8. The formula is `1e6 * mean_pollen / (PM10 + superPM10)` on fully covered, exactly matched collection periods. The seven ratios are descriptive number-to-mass measurements, not a pollen mass fraction. No nested masses are added.

The actual one-button MyBinder run completed all five production jobs in **10.0 minutes**, including first-run preparation. All numerical reference checks, seven pollen ratios, 282 exported assets and the exact flowchart passed. All 37 launcher, 54 scientific and 32 orchestration tests passed; an independent review found no remaining material issues. See [POLLEN_VALIDATION.json](POLLEN_VALIDATION.json). The earlier `binder-20261019-no-backscatter-r1` implements the author's 19 October 2026 scope revision. It removes **62 historical figures and 115 assets**, including mixed plots containing backscattering coefficients, backscattering fractions, related uncertainty/baseline diagnostics and their companion formats. Mass-only comparisons with historical selection rules are retained because they do not plot those quantities.

Figure 1 is the **exact 5811 × 4250 PNG** from `manuscripts_significant_figures_20261019.zip`, member `figures/main/figure_1.png`. Its SHA-256 is `758441e4dcbd98788cf03024e3acd2c4f3bf0ec1c131d9238936aeed4b900c8e`. It is copied without redraw or resampling, including in full analysis exports. The same image is supplied in the code and data archives. Pollen corroboration checks remain active.

The original registered scientific code already omitted backscattering-specific routines. The revised code archive keeps the numerical calculations and removes obsolete alternate flowchart artwork/source. Numerical observations and numerical reference tables are unchanged; the data archive now also includes the current pollen figure and renumbers the two following reference images. All 113 retained historical images and companion formats preserve their original bytes.

For the earlier seven-figure release, the actual MyBinder button completed all five production jobs in **9.9 minutes**, including initial archive preparation, with the original 5,000/2,000 draws and all numerical reference checks. All **37 launcher tests and 21 renderer tests** passed. The complete 130-figure/281-asset download passed integrity checks; all other retained assets matched the earlier completed production run. The manuscript flowchart matched exactly. A distribution scan of all **39 scientific Python files, 15 launcher Python files and notebook code cells** found zero references to the excluded quantities, including their abbreviations.

Earlier scope verification is recorded in [SCOPE_VALIDATION.json](SCOPE_VALIDATION.json). The detailed removal list, source hashes and code audit are in [audit/scope_revision.json](audit/scope_revision.json); the fixed-artwork code change is in [audit/renderer_artwork.diff](audit/renderer_artwork.diff). Earlier 192-figure tests remain historical evidence in [ONE_CLICK_VALIDATION.json](ONE_CLICK_VALIDATION.json) and [FULL_ANALYSIS_VALIDATION.json](FULL_ANALYSIS_VALIDATION.json). See [VALIDATION.md](VALIDATION.md).

The first deliberate button click downloads and verifies the three supplied archives before calculation. They are prepared in temporary session storage. The Binder image contains the pinned software, which keeps startup independent of a large data layer.

## Local use

Extract this launcher's ZIP once and keep the three matching archives in a separate directory. Use an isolated Python 3.12.14 environment with Jupyter installed:

```bash
python -m pip install -r .binder/requirements.txt -r .binder/ui-requirements.txt
python -m pip check
python prepare_release.py --destination runtime \
  --codes-zip ../archives/codes.zip \
  --data-zip ../archives/data.zip \
  --figures-zip ../archives/additional_figures.zip
voila One_click.ipynb
```

Use a fresh runtime directory when upgrading from a previous archive identity. Existing unrelated or modified prepared releases are refused. All archive sizes/hashes, the 342-file data check and every additional asset are verified before use.

For code inspection or quick rendering from saved inputs, run `jupyter lab Start_here.ipynb`. The advanced notebook leaves `RUN_FULL_ANALYSIS = False` until deliberately enabled. The one-button page runs the full workflow after its button click, using `--language python --all-methods --size-bootstrap --native-size-bootstrap`, with the original 5,000 bootstrap and 2,000 year-block draws and all numerical reference checks. Each run creates a fresh output directory.

## Scientific scope

The current pipeline recalculates the registered Python analyses from supplied processed observations. Raw instrument corrections and original category attribution remain upstream. Figure 1 is fixed artwork; 17 current figures are recomputed. The 113 historical figures retain their original methods and cohorts and are labelled `archived_image`; their original pipelines are not rerun by this launcher. The gallery and ZIP preserve these distinctions. The current release's SI renderer has no separate embedded figures; additional scientific images are included through the gallery inventory.

Python 3.12.14 and the original 16 scientific dependency pins are preserved. Voilà 0.5.13 and ipywidgets 8.1.9 provide the one-button page. See the official [Binder usage/resource guidelines](https://mybinder.readthedocs.io/en/latest/about/user-guidelines.html).

## Archive identities

| Archive | Bytes | SHA-256 |
|---|---:|---|
| codes.zip | 2,307,358 | `732e020a6f1df1fff4299ebdac4bc611f58635f0625a4827bb53861cca2b75d8` |
| data.zip | 374,791,899 | `7eb650fb02b403430cf8f55f234311112573f56b781386f96890ffe2cd555826` |
| additional_figures.zip | 39,053,830 | `c2ab4189b28cba1b5a889c9715ecdf6249234ddb7776e7812c7a0c7972224d14` |

These revised archives use release [`binder-20261019-pollen`](https://github.com/sujaibanerji/hyytiala-binder-reviewer/releases/tag/binder-20261019-pollen). Earlier releases remain versioned records. No DOI is assigned by this GitHub release. Launcher checksums are delivered separately in `SHA256SUMS.txt`.

## Source audit

[figure_inventory.json](figure_inventory.json) lists retained figures, captions, placements and identities. [figure_exclusions.csv](figure_exclusions.csv) records overlap decisions and explicit scope exclusions. [audit/selection_decisions.json](audit/selection_decisions.json) retains the source-level audit. The earlier 6,210-source scan is supplemented by the newly supplied flowchart; excluded backscattering content has no active gallery asset or code registration. See [audit/README.md](audit/README.md).

When committing a launcher snapshot, preserve the executable Git mode of `.binder/postBuild`. The public repository excludes local development history and machine paths.
