# Current manuscript and SI figure reproduction

This release uses the revised `data.zip` and `codes.zip` dated 25 October 2026.
It reproduces eight main-manuscript and three supplementary figures, including
the tighter boxplot axes, numeric collection counts and the Figure 2 explanation
of n. Data observations and statistical definitions are unchanged.

The default workflow redraws the figures from frozen processed inputs, preserves
Figure 1 artwork, and recalculates the dust diagnostic. It does not reconstruct
instrument observations or recalculate the saved uncertainty intervals.

`One_click.ipynb` starts automatically in Voilà. Keep the tab open and download
results before leaving; Binder storage is temporary. Optional historical
recomputation is available after the default workflow finishes.

Archive URLs, sizes and SHA-256 checksums are fixed in `binder_release.json`.
A missing or mismatched archive causes an error; an older release is never used.
The hosted run is awaiting verification. See the release page for final status.

For local use, extract binder.zip into binder/ beside the two archives, install
the requirements in `.binder/`, and run:

```sh
python binder/launcher.py --archive-dir . --offline --output-dir results/new_run
```
