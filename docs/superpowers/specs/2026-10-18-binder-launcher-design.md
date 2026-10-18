# Binder launcher for the Hyytiälä reviewer package

Status: approved by the user on 18 October 2026, including all distinct scientific figures and removal of overlapping versions.

## Purpose and agreed direction

Reviewers should be able to open a browser notebook, verify the matching code and data release, inspect every distinct scientific image from the main manuscript, supplementary information, and the wider supporting analysis, and choose whether to run the full Python analysis. They should not need an account or install software. The user's latest selection rule is to include all images except overlapping images: remove redundant versions while preserving figures that add different scientific content. A subset of main-manuscript figures does not meet the requirement.

The initial delivery is a local launcher package and Linux validation evidence. Public release needs the final version-specific archive URLs and a confirmed publication destination. The existing scientific archives remain the inputs to the launcher.

## Source release

Use the existing release 20261015 in:

`zenodo_reviewer_package_20261015/` (the original local reviewer package; source-root mapping stays outside the public repository)

| Archive | Bytes | SHA-256 |
| --- | ---: | --- |
| codes.zip | 1,758,048 | da54154e80123d73818f8421a5fe3055effa154839648e0740eb0b59e61ee83b |
| data.zip | 373,657,528 | c86ec82967021950bbd4b59c8ee3dbf133af6d89170a040a6957e731687d99b3 |

Both ZIPs contain their contents directly. Extract them into sibling `codes/` and `data/` directories. The data expand to 942,449,887 bytes; that is disk usage, not measured RAM consumption. Source redistribution status is recorded in the original release documents and is not changed by this launcher.

## Approach and alternatives

Use a small GitHub launcher repository with Binder configuration and a guided notebook. Download and verify the archives during `postBuild`, so their extracted contents are included in the cached image. This increases image size but avoids a repeated 374 MB download in each reviewer session.

Downloading on demand in each notebook session would keep the image smaller but add waiting time to each launch. A combined new archive on Zenodo could support a different packaging approach, but would require assembling and maintaining an additional release. The separate launcher reuses the existing archive identities.

## Files and data flow

The launcher contains:

- `.binder/environment.yml`: Python 3.12.14 with the existing exact scientific dependency pins installed through pip. Check and record the actual runtime; do not silently substitute another patch version.
- `.binder/requirements.txt`: the 16 original scientific pins, copied exactly from `codes.zip`.
- `.binder/postBuild`: run the preparation script and stop on failure.
- `binder_release.json`: release identities, archive sizes, SHA-256 values, and version-specific HTTPS URLs for the original archives and the additional figure bundle. URL fields remain unset in local preparation mode until the publication details are supplied; a network build must fail clearly when they are unset.
- `prepare_release.py`: prepare from explicit local archive paths or the configured public URLs, verify archives before extraction, run the original data-integrity checker, and check the additional figure bundle against its inventory.
- `additional_figures.zip`: an additive bundle of the distinct additional figures selected by the audit, their captions, source identities, and source-code/input provenance. The original `codes.zip` and `data.zip` remain unchanged. Keep the bundle outside Git; fetch it alongside the original archives during the Binder build.
- `figure_inventory.json` and `figure_exclusions.csv`: the canonical figure list and the source-copy decisions, including each figure's availability for fresh calculation versus archived-image viewing.
- `Start_here.ipynb`: reviewer instructions, integrity check, rendering and viewing of the complete figure inventory, optional full calculation, and result downloads.
- `README.md`: local preparation, validation, publication inputs, and the eventual commit-pinned Binder launch link.
- Focused tests for preparation failures and notebook execution.

Local source paths are supplied as command arguments and are excluded from publishable configuration. Scientific data, extracted code, virtual environments, generated figures, and local validation outputs are excluded from Git. Preparation uses separate temporary staging, rejects unsafe archive paths, and refuses to replace an unrelated existing extraction. A matching prepared release can be reused after validation.

## Packaged figure inventory and wider project audit

The current packaged main-manuscript and supplementary-information TeX sources, renderer entry points, release receipt, and completed Python output directory establish this inventory:

| Group | Required output images |
| --- | ---: |
| Main manuscript | 7 |
| Embedded supplementary-information figures | 0 |
| Separate supporting figures | 10 |
| Currently registered package outputs | 17 |

These 17 images are the verified package baseline, not a final ceiling for the Binder scope. Include distinct scientific plots from the wider source project, including earlier manuscript/SI figures and diagnostics when they add content. Audit source-data compatibility and whether figures are current, historical, superseded, or diagnostic. Keep historical figures with distinct content explicitly labelled and separate from current results. A figure is not omitted solely because it is absent from the current ZIPs or was not embedded in a manuscript. Styling previews, dummy examples, duplicate formats, and rendered document pages are not separate scientific outputs.

The source-project audit covers `outputs/Hyytiala_four_category` beneath the established source workspace and the verified completed package outputs. The initial PNG index is recorded in `work/figure_audit/png_source_index.json`. Its initial scan found 1,987 PNG candidates and 453 repeated byte-identical copies after excluding the named QA/render/history folders. These are file-audit counts, not a final count of distinct scientific figures. The full audit must also locate scientific images in excluded history folders and other file formats, then compare them with the retained canonical figures so a unique historical result is not missed.

### Rules for removing overlap

1. **Identical images:** keep one canonical image when SHA-256 or decoded-pixel equality establishes identical content. Record all alternate paths.
2. **Duplicate formats and presentation variants:** one scientific image may have PNG, SVG, and PDF exports or several colour, font, resolution, or layout revisions. Give it one gallery entry, retaining available useful download formats. Prefer the current verified presentation.
3. **Repeated manuscript and supporting placements:** if the same figure appears in several documents or draft directories, show it once and record every placement.
4. **Superseded versions of the same analysis:** prefer the current verified version when an earlier plot answers the same question with superseded processing. Record the earlier version as an excluded predecessor, with the chosen replacement.
5. **Different scientific content:** preserve figures with different variables, wavelengths, fractions, collection cohorts, seasons, adjustments, uncertainty methods, temporal resolution, or diagnostic questions. Similar appearance alone does not establish overlap.
6. **Composite figures:** prefer the current complete composite over standalone panels that add nothing. Keep a partially overlapping figure if it contains additional scientific information not otherwise retained. Do not crop or modify scientific plots merely to force deduplication.
7. **Ambiguous cases:** inspect the images together with their captions, data identities, and generating scripts. Do not use a perceptual-image similarity threshold as the sole reason to exclude a figure. Keep an unresolved candidate in the review inventory until its content is resolved.

Record every included figure and every excluded source copy in an audit table. Each exclusion must name its canonical replacement or identify the item as a QA/mockup/document-render artifact. The final gallery must have no unresolved overlap decisions.

The additional figure families found on 18 October include wavelength-specific category distributions, hourly/monthly optical time series, seasonal sampling and adjustment plots, pollen timing and interval comparisons, mass-quality timelines, optical-source overlap diagnostics, and size distributions for different collection cohorts. Earlier backscattering and backscatter-fraction plots require special attention because later manuscript revisions excluded those measurements. Earlier size plots also use geometric conventions that differ from the current projected-area curves; do not mix their values or labels.

The main-manuscript images are `figure_1.png` through `figure_7.png`. Include Figure 1's fixed conceptual artwork and Figure 7's uncertainty plot along with the other five figures.

The supporting images are:

- `effect_sca550.png`
- `effect_abs550.png`
- `effect_ssa550.png`
- `effect_msc550.png`
- `effect_mac550.png`
- `effect_sae.png`
- `effect_aae.png`
- `effect_PM_mass.png`
- `diagnostic_ranking.png`
- `diagnostic_bubbles.png`

The current SI entry point explicitly reports zero embedded figures. Its supporting numerical calculations and tables remain included in the full workflow. Do not invent SI figures or omit a supporting figure merely because it is not embedded in either document. Audit document image references and all registered figure outputs against this inventory; flag any unmatched required image rather than silently skipping it. Supporting image labels and grouping must follow the recorded source provenance.

## Reviewer notebook

The notebook opens with a short explanation of the processed-data boundary and two distinct activities:

1. **Render and view the complete inventory:** use the original renderer for all seven main-manuscript figures and the original supporting renderer for all ten supporting figures. Both supporting-renderer inputs, `reference/bootstrap_summary.csv` and `reference/legacy/diagnostic_ranking.csv`, are present in the existing data ZIP. This path uses supplied processed observations and saved derived tables, so it must be labelled accordingly. Figure 1 uses its declared fixed-artwork rendering or fallback. Figure 7 and the supporting effect plots use saved interval estimates on this path; do not claim new bootstrap calculations. Retain the existing provenance manifests and add an explicit wrapper record identifying saved reference estimates. Preserve the paired area and volume distributions in Figure 6. Load the additional selected figures from the verified additive bundle and show their original scope, captions, and source identities in the same gallery.
2. **Recalculate the registered analyses:** an explicit optional action invokes the existing `run_all.py` with production settings, including `--all-methods --size-bootstrap --native-size-bootstrap`. This regenerates all seven main figures and all ten supporting figures from the workflow's newly computed exports, while retaining the declared fixed-artwork scope of Figure 1. The additional-image audit must identify the original generating code and required inputs for each retained figure. Register additional generation commands only when those inputs and scripts are portable and validated. If a retained historical figure can only be provided as an archived image, state that directly; do not imply that the current 17-figure launcher recalculates it. Use a new output directory for every run. Show job progress and logs, retain the original scope reports, and report success only after the requested registered jobs, reference checks, and corresponding figure-inventory checks finish successfully.

Display every image in the finalized audited inventory in a browsable gallery with filenames, group labels, and its estimate origin. This includes at least the 17 currently registered package outputs and every additional relevant figure admitted by the source-project audit. Offer individual images and a download containing the entire figure set and its manifests. A successful rendering action must account for every expected output. Do not deliver only Figures 2–6 or treat supporting plots as optional omissions.

Heavy calculations do not start merely by opening the notebook or by running its normal introductory cells. Use a separate opt-in control for the full run. The full calculation option covers the same current, reproducible figure inventory as the saved-input rendering path. Any historical images retained for context must show their original provenance and must not be represented as current regenerated results. Offer downloading results before the ephemeral session ends.

Julia remains available in the original download. Installing and validating Julia inside Binder is a later extension; the initial online environment is Python-only.

## Validation and acceptance

Validate the preparation script with matching local archives, an altered archive, missing source configuration, an interrupted or failed download, and an existing unrelated destination. Test archive validation and extraction without changing the source ZIPs.

Use the installed WSL Ubuntu environment to create a separate Python 3.12.14 environment, install the scientific pins, check dependencies, verify the data, and execute the notebook's complete saved-input rendering path. WSL currently provides Python 3.12.3; obtain the specified runtime in the separate environment before calling this a matching-runtime test. Confirm all 17 registered output filenames plus every additional audited gallery item, open and inspect every retained image, and check the provenance reports and full-set download. Verify all additional archived assets against their manifest and test every added regeneration command before labelling it reproducible. Measure elapsed time and peak memory for that path where supported. This establishes Linux execution only for the commands actually run.

Run the existing full production entry point once under the Linux environment during validation. Verify all 17 generated figures and the numerical reference checks, retaining logs and scope manifests. Its earlier Windows success and 43.5-minute duration are historical execution evidence; the new Linux test must stand on its own results. If a runtime or resource limitation prevents that run from completing, keep the implementation explicitly unverified for full Linux regeneration and report the limitation.

An actual Binder build and complete saved-input notebook execution are the final online acceptance checks after publication inputs are available. WSL execution cannot establish Binder memory limits or launch success. A full production rerun within MyBinder remains separately subject to its resources; access to every current figure in the finalized audited inventory through the saved-input path is required regardless. Report the exact checks completed and retain the original scientific scope limits.

## Publication handoff

The GitHub CLI is authenticated as `sujaibanerji`; Ubuntu is available through WSL. No new account is needed for local preparation. The local workspace is not currently a Git repository. A local Git repository can be initialized during implementation so the reviewed design, code, and subsequent validation can be versioned together.

Before a public launch, resolve the final URLs for all required archives, including the additive figure bundle; confirm the intended public repository and archive visibility; and prepare the exact files and changes for review. Keep account credentials out of the launcher. Use immutable archive versions and a commit-pinned Binder link once the online build passes.

## Official references

- [Binder repository requirements](https://mybinder.readthedocs.io/en/latest/introduction.html)
- [repo2docker environment configuration](https://repo2docker.readthedocs.io/en/latest/configuration/research/)
- [Binder build-time preparation](https://mybinder.readthedocs.io/en/latest/using/using.html)
- [MyBinder resource limits](https://mybinder.readthedocs.io/en/latest/user-guidelines.html)
