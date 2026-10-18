# Hyytiälä reviewer figures for Binder

This launcher presents **192 distinct scientific figures**: seven current main-manuscript figures, ten current supporting figures and 175 archived historical figures. The packaged supplementary information has no embedded figures. Available companion formats bring the complete download to 396 image assets.

[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://gesis.mybinder.org/v2/gh/sujaibanerji/hyytiala-binder-reviewer/560c4e3264d217ca106818318ec03b6aecb0224e?urlpath=lab/tree/Start_here.ipynb)

**[Launch the tested notebook](https://gesis.mybinder.org/v2/gh/sujaibanerji/hyytiala-binder-reviewer/560c4e3264d217ca106818318ec03b6aecb0224e?urlpath=lab/tree/Start_here.ipynb)**, then choose **Run → Run All Cells**. Browse the gallery in the notebook or download the result ZIP when rendering finishes. This link pins the exact tested commit. The [standard MyBinder link](https://mybinder.org/v2/gh/sujaibanerji/hyytiala-binder-reviewer/560c4e3264d217ca106818318ec03b6aecb0224e?urlpath=lab/tree/Start_here.ipynb) is also available. The standard browser route returned 403 during the 18 October test; this update was tested through the direct GESIS provider above.

Open `Start_here.ipynb` and run the normal cells to render the current 17 figures, browse the entire gallery and download individual images or the complete ZIP. The normal path uses processed observations and saved derived tables. Saved uncertainty estimates are labelled `saved_reference`; Figure 1 is fixed artwork. Historical figures retain their original cohorts, processing and geometry conventions and remain labelled `archived_image`.

Reviewers do not need a Binder account. Binder sessions have temporary storage, so download results before leaving. See the official [Binder usage guidelines](https://mybinder.readthedocs.io/en/latest/about/user-guidelines.html).

## Current delivery status

**Binder version `binder-20261019`**, tested on **19 October 2026**, fixes all three previously deferred minor issues: the IPython display advisory, the production-gallery introduction and the offline gallery's external ZIP link. All **30 focused Linux tests** passed, including the three regressions observed failing before the fixes.

The new commit passed an actual MyBinder build, the complete normal notebook and browser image/download checks. It provides **192 distinct figures and 396 image assets**, using Python 3.12.14 and all 16 exact scientific package versions. Run All skips the optional full calculation. The browser-downloaded ZIP passed CRC, all asset hashes and every portable HTML download-link check. See [VALIDATION.md](VALIDATION.md) and [ONLINE_VALIDATION.json](ONLINE_VALIDATION.json).

This build and launch took about 4.5 minutes; normal notebook execution took about 16 seconds in the test session. These are observations, not timing guarantees. The badge and launch links pin the tested code commit `560c4e3264d217ca106818318ec03b6aecb0224e`; the `binder-20261019` Git tag identifies that version.

## Local preparation

Keep the original `codes.zip` and `data.zip`, plus the additive `additional_figures.zip`, in a separate archive directory. Extract the launcher ZIP once. From that launcher directory, use an isolated Python 3.12.14 environment with Jupyter installed, then install the exact scientific dependencies:

```bash
python -m pip install -r .binder/requirements.txt
python -m pip check
python prepare_release.py --destination runtime \
  --codes-zip ../archives/codes.zip \
  --data-zip ../archives/data.zip \
  --figures-zip ../archives/additional_figures.zip
jupyter lab Start_here.ipynb
```

Use the same interpreter/kernel for installation and notebook execution. Jupyter is supplied by repo2docker online; the scientific requirements file preserves the original release's 16 exact pins. Archive byte sizes and SHA-256 hashes are checked before extraction. Preparation also runs the original 341-file data check and validates every additional asset. Matching verified releases can be reused; unrelated or changed destinations are refused. Use a fresh destination if a prepared release has changed.

## Optional production calculation

Online execution covers the Python workflow.

The final notebook cell has `RUN_FULL_ANALYSIS = False`. Run All leaves it disabled. To deliberately calculate the current production analyses, change that value to `True` and run the cell. This invokes the unchanged release launcher with `--language python --all-methods --size-bootstrap --native-size-bootstrap`, retaining defaults of 5,000 bootstrap draws and 2,000 year-block draws, plus the numerical reference checks. Each run uses a fresh analysis directory and retains progress, original logs and scope manifests. An additive compatibility wrapper preserves a symlinked Linux virtual environment for child jobs; it changes no scientific source or archive.

The current 17 figures are regenerated from supplied processed inputs. Raw instrument corrections and original category attribution remain upstream. Historical figures are included as archived images; this current pipeline does not recreate their original historical analyses. The gallery and ZIP preserve these distinctions.

MyBinder guarantees at least 1 GB RAM and allows at most 2 GB, and intensive sessions are subject to an approximately one CPU-hour limit. These are service policies, not a successful online test of this launcher. Use a local environment if the optional long calculation exceeds available session resources. See [official resource limits](https://mybinder.readthedocs.io/en/latest/about/user-guidelines.html#resources-available).

## Figure provenance and overlap decisions

`figure_inventory.json` lists every retained figure, source placements, captions, byte identities, original scope and regeneration status. `figure_exclusions.csv` links excluded scientific versions to retained counterparts. `audit/selection_decisions.json` accounts for all 6,210 source candidates. See [the audit record](audit/README.md).

The audit preserves distinct wavelengths, populations, adjustments and diagnostic questions. Current figures replace overlapping earlier versions; historical results with different content remain. Companion PDF/SVG files come from the same source run and plot stem. The additional bundle preserves original image bytes and records related source-code identities where available; these references are not claims of validated historical regeneration.

## Archive identities

| Archive | Bytes | SHA-256 |
|---|---:|---|
| codes.zip | 1,758,048 | `da54154e80123d73818f8421a5fe3055effa154839648e0740eb0b59e61ee83b` |
| data.zip | 373,657,528 | `c86ec82967021950bbd4b59c8ee3dbf133af6d89170a040a6957e731687d99b3` |
| additional_figures.zip | 66,991,173 | `66b437b3740fa724de6155a133fa766cd0296934cbdcc1047f61f60314174ef9` |

The two original ZIPs are unchanged. The additive bundle contains 175 canonical archived images plus 204 companion PDF/SVG exports. Launcher artifact checksums are delivered separately in `SHA256SUMS.txt`.

## Publication handoff

Public repository: [sujaibanerji/hyytiala-binder-reviewer](https://github.com/sujaibanerji/hyytiala-binder-reviewer). The three matching archives use release `reviewer-20261015-binder-20261018`. The author approved public publication on 18 October 2026. No DOI is assigned by this GitHub release.

The published repository starts from the reviewed, allowlisted launcher snapshot; local development history is excluded. The release preserves the three exact archive identities above. Online acceptance checked downloaded archive hashes, an actual MyBinder build and the complete 192-figure normal notebook. The launch links above pin the tested immutable commit; subsequent documentation updates do not change that tested environment.

When committing an extracted launcher snapshot, preserve the executable Git mode for `.binder/postBuild` (`git update-index --chmod=+x .binder/postBuild` after adding it).

For environment configuration, see the official [repo2docker research configuration](https://repo2docker.readthedocs.io/en/latest/configuration/research/).
