# Hyytiälä one-click release: `binder-20261019-dust-evidence`

This folder is the **Git repository root** to commit for the new launcher. It
contains real Binder configuration, notebook and code, but no `.git`, scientific
data or nested code/data archives. Extract `binder.zip` into this root once.
The root is small enough for a source-tree API upload.

## One click, with explicit scope

Open `One_click.ipynb` in Voilà: the default starts automatically, with no Run click.
It obtains only the exact configured new code/data archives, checks size,
SHA-256, ZIP CRC and safe extraction, and runs the four current Python entrypoints.
Figures 2–8 are redrawn from frozen saved/processed numerical inputs. Figure 1
is the exact supplied current workflow artwork. The new dust overlap/count/
median/Cliff exports are recomputed from an immutable snapshot. Supporting r6
tables/figures remain labelled historical. Default saved uncertainty intervals
are displayed, not newly bootstrapped.

After success only, optional manual controls reveal the **Also recompute
historical r6 processed-input analysis** checkbox and a separate rerun button.
Selecting that option and explicitly rerunning adds the unchanged r6 full
processed-input workflow first (5,000/2,000 draws).
It is not a full original-instrument-data rerun. Its outputs are separate;
its settings do not update the frozen current-figure snapshot. Both modes end
with the current eight-figure gallery and a results ZIP. Current rendering and
dust replay use Python; Julia wrappers do not imply independent new validation.

One controller is reused per notebook kernel: re-rendering or re-executing
`show()` does not start another run, even after failure. Progress/errors remain
visible. Retry appears only after failure and always requires an explicit click.
Optional historical settings are hidden and disabled until success. A new kernel
is a new session and starts once again; do not refresh to retry. This is not
cross-kernel or server-wide deduplication. The worker runs in the background so
the landing/progress widgets can render without waiting for calculations.

## Local headless equivalent

Place matching `codes.zip` and `data.zip` beside `binder/` (or specify a folder).
Install Python 3.12.14 and `.binder/requirements.txt`; UI packages are needed only
for notebook/Voilà use. Then:

```sh
python -B binder/launcher.py --archive-dir . --offline --output-dir results/binder_01
# Explicit historical recomputation as well:
python -B binder/launcher.py --archive-dir . --offline --output-dir results/full_01 --historical-recompute
python -B binder/test_launcher.py
```

No existing output/runtime directory is reused. Missing/bad new archives fail
clearly; there is no silent old r6 URL or data fallback. In online use the exact
URLs in `binder_release.json` are used. Downloads occur at run time, not during
the image build. `.binder/postBuild` installs exact scientific and UI pins.

## Publication handoff — do not invent a commit

Prepared branch: `release/dust-evidence-20261019`.
Prepared tag: `binder-20261019-dust-evidence`.
Repository: `sujaibanerji/hyytiala-binder-reviewer`.
Upload these exact assets to that tag's GitHub release:
`data.zip`, `codes.zip`, `binder.zip`. Code/data expected sizes, SHA-256 and
release-download URLs are in `binder_release.json`. No mutable `latest` URL.

After the main agent publishes and verifies that tag, the planned launch URL is:

`https://mybinder.org/v2/gh/sujaibanerji/hyytiala-binder-reviewer/binder-20261019-dust-evidence?urlpath=voila/render/One_click.ipynb`

Click the Binder link once, then wait. Everything will start automatically. Keep the tab open; do not click Run, change settings, or refresh the page. The figures and download links will appear when processing finishes.

The initial Binder build and archive downloads may take several minutes before
the Voilà landing/progress UI becomes available. These instructions must also
accompany the link outside the app; the app cannot show them before it loads.

Local UI-contract tests: `python -B test_one_click.py` (mocked widgets/runner,
no cloud claim). Existing six launcher tests remain unchanged.

For the strongest immutable launch identity, replace the tag in that URL with
the **actual commit SHA returned by publication**, never an invented commit.
Until the tag and assets exist, this is a recipe, not a verified live service.
Local tests do not certify a completed MyBinder/Voilà cloud run. Binder capacity,
builds and session lifetime are external; download results before closing.

If hosting changes, run `python configure_release.py --base-url EXACT_HTTPS_BASE`
to change URLs while retaining hash/size pins, then commit that configuration
and use its new real commit identity. Republishing different bytes under the
same pinned identity is not supported.

## Historical material

New data/code preserve the r6 scientific inputs, native Python/Julia source,
numerical reference diagnostics and calculation logs. Old cloud validation is
explicitly historical. The optional old additional-figure archive is listed
separately in `historical_optional.json`; it is never downloaded or run by default
and does not stand in for current figures. No manuscript drafts, article
documents, administrative plans or account credentials belong in this Git root.
