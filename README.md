# Hyytiälä manuscript analysis and figures

This Python code accompanies the manuscript and its supplementary information. The current gallery contains **130 distinct scientific figures and 281 image assets**: seven main-manuscript figures, ten current supporting figures and 113 archived historical figures.

[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://gesis.mybinder.org/v2/gh/sujaibanerji/hyytiala-binder-reviewer/binder-20261019-no-backscatter?urlpath=voila/render/One_click.ipynb)

**[Open Binder](https://gesis.mybinder.org/v2/gh/sujaibanerji/hyytiala-binder-reviewer/binder-20261019-no-backscatter?urlpath=voila/render/One_click.ipynb)**, then click **Run full analysis**. Progress, the gallery and downloads appear on the same page. Reviewers do not need an account or notebook editing.

Estimated calculation time is **10–30 minutes**, depending on the Binder server, with about five minutes for initial startup. Calculation runs on Binder's servers; internet speed mainly affects page loading and downloads. These are estimates, not guarantees. Download results before leaving because Binder storage is temporary.

## Current version

`binder-20261019-no-backscatter` implements the author's 19 October 2026 scope revision. It removes **62 historical figures and 115 assets**, including mixed plots containing backscattering coefficients, backscattering fractions, related uncertainty/baseline diagnostics and their companion formats. Mass-only comparisons with historical selection rules are retained because they do not plot those quantities.

Figure 1 is the **exact 5811 × 4250 PNG** from `manuscripts_significant_figures_20261019.zip`, member `figures/main/figure_1.png`. Its SHA-256 is `758441e4dcbd98788cf03024e3acd2c4f3bf0ec1c131d9238936aeed4b900c8e`. It is copied without redraw or resampling, including in full analysis exports. The same image is supplied in the code and data archives. Pollen corroboration checks remain active.

The original registered scientific code already omitted backscattering-specific routines. The revised code archive keeps the numerical calculations and removes obsolete alternate flowchart artwork/source. Numerical observations and numerical reference tables are unchanged; the data archive changes only Figure 1 and its checksum record. All 113 retained historical images and companion formats preserve their original bytes.

Current verification is recorded in [NO_BACKSCATTER_VALIDATION.json](NO_BACKSCATTER_VALIDATION.json). The detailed removal list, source hashes and code audit are in [audit/scope_revision.json](audit/scope_revision.json); the fixed-artwork code change is in [audit/renderer_artwork.diff](audit/renderer_artwork.diff). Earlier 192-figure tests remain historical evidence in [ONE_CLICK_VALIDATION.json](ONE_CLICK_VALIDATION.json) and [FULL_ANALYSIS_VALIDATION.json](FULL_ANALYSIS_VALIDATION.json). See [VALIDATION.md](VALIDATION.md).

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

Use a fresh runtime directory when upgrading from a previous archive identity. Existing unrelated or modified prepared releases are refused. All archive sizes/hashes, the original 341-file data check and every additional asset are verified before use.

For code inspection or quick rendering from saved inputs, run `jupyter lab Start_here.ipynb`. The advanced notebook leaves `RUN_FULL_ANALYSIS = False` until deliberately enabled. The one-button page runs the full workflow after its button click, using `--language python --all-methods --size-bootstrap --native-size-bootstrap`, with the original 5,000 bootstrap and 2,000 year-block draws and all numerical reference checks. Each run creates a fresh output directory.

## Scientific scope

The current pipeline recalculates the registered Python analyses from supplied processed observations. Raw instrument corrections and original category attribution remain upstream. Figure 1 is fixed artwork; 16 current figures are recomputed. The 113 historical figures retain their original methods and cohorts and are labelled `archived_image`; their original pipelines are not rerun by this launcher. The gallery and ZIP preserve these distinctions. The current release's SI renderer has no separate embedded figures; additional scientific images are included through the gallery inventory.

Python 3.12.14 and the original 16 scientific dependency pins are preserved. Voilà 0.5.13 and ipywidgets 8.1.9 provide the one-button page. See the official [Binder usage/resource guidelines](https://mybinder.readthedocs.io/en/latest/about/user-guidelines.html).

## Archive identities

| Archive | Bytes | SHA-256 |
|---|---:|---|
| codes.zip | 2,303,874 | `6e76f237634165f9a331260523482957bac3f6838ac929ff1e8c4bd360fc0447` |
| data.zip | 374,534,368 | `eb3fa491aff7cdcdd5fb4c59568c24f47f26c452796ec8b210bad6d74c1eeffa` |
| additional_figures.zip | 39,053,830 | `c2ab4189b28cba1b5a889c9715ecdf6249234ddb7776e7812c7a0c7972224d14` |

These revised archives use release [`binder-20261019-no-backscatter`](https://github.com/sujaibanerji/hyytiala-binder-reviewer/releases/tag/binder-20261019-no-backscatter). Earlier releases remain versioned records. No DOI is assigned by this GitHub release. Launcher checksums are delivered separately in `SHA256SUMS.txt`.

## Source audit

[figure_inventory.json](figure_inventory.json) lists retained figures, captions, placements and identities. [figure_exclusions.csv](figure_exclusions.csv) records overlap decisions and explicit scope exclusions. [audit/selection_decisions.json](audit/selection_decisions.json) retains the source-level audit. The earlier 6,210-source scan is supplemented by the newly supplied flowchart; excluded backscattering content has no active gallery asset or code registration. See [audit/README.md](audit/README.md).

When committing a launcher snapshot, preserve the executable Git mode of `.binder/postBuild`. The public repository excludes local development history and machine paths.
