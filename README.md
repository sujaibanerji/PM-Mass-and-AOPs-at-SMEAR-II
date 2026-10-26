# SMEAR II reproduction — 27 October 2026

Package revision: **20261027-self-contained**. Use this Binder folder with the matching `codes.zip` and `data.zip`; their exact sizes and SHA-256 hashes are recorded in `binder_release.json`.

## Run locally

Keep the three ZIPs together and extract `binder.zip` into `binder/` beside `codes.zip` and `data.zip`. With Python 3.13, install the numerical requirements from `binder/.binder/requirements.txt`. To use the notebook interface, also install `binder/.binder/ui-requirements.txt` and `binder/.binder/security-requirements.txt`.

From their common parent directory:

```text
python binder/launcher.py --archive-dir . --offline --output-dir results/new-run
```

For the automatic interface, launch `binder/One_click.ipynb` with Voilà in Jupyter Server. The interface starts once per kernel, shows progress, displays errors, and offers an explicit retry after failure. Download the results before leaving a hosted session. Each new run needs a fresh output directory.

## What is reproduced

The automatic default redraws Figures 2–8 and S1–S3 from frozen saved/processed inputs, copies the exact Figure 1 asset, and recomputes the dust diagnostic. It checks all 11 figures against matching references. Saved bootstrap intervals are retained. The optional historical control reruns the historical r6 processed-input analysis separately; it does not change the frozen current-figure inputs.

The matching archives also contain the supplemental analysis sources, inputs and references. Extract `codes.zip` into `codes/`, leave both ZIPs beside that directory, and run:

```text
python codes/run_supplemental.py --archive-dir . --output-dir "supplemental results"
```

These commands do not reconstruct measurements from original instrument files. See the code archive's documentation for each analysis and its output comparisons.

## Binder startup repair

The previous dependency pin `tornado==6.5.9` caused Voilà 0.5.13 to reject its own JavaScript and stylesheets with HTTP 403. The browser therefore stayed at “Executing 2 of 2” although the notebook worker could run. The repair pins `tornado==6.5.10`, the upstream compatibility fix. It preserves path-traversal protection and the existing background worker and duplicate-run guards.

The problem was reproduced in a fresh hosted session of commit `ff218d82cecbc95833df982759320d6c58453bb3` and locally in Chrome. The repaired local browser displayed progress while work continued and displayed an intentional failure with its retry control. `test_static_assets.py` exercises the actual HTTP handlers; `.binder/postBuild` runs this check before a new image is accepted. [Tornado 6.5.10 release notes](https://www.tornadoweb.org/en/stable/releases/v6.5.10.html) describe the Jupyter compatibility repair.

`BINDER-STARTUP-VERIFICATION.json` records the new startup evidence. The older `HOSTED_VERIFICATION*.json` files are historical receipts for earlier packages; they do not verify the current browser or current archives. A new hosted receipt must identify the exact published source commit and matching archive hashes.
