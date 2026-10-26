# SMEAR II manuscript and supplementary figures

## Absorption and MAC at 520 nm

This release uses absorption and MAC at 520 nm. Scattering, MSC and SSA remain at
550 nm; SSA uses absorption matched to 550 nm. The archives contain the revised
figures, numeric formatting, collection counts and Figure 6 calendar display.

Hosted verification is pending. The source will be pinned after a successful
automatic-start Binder test. Matching archives are in the
[release](https://github.com/sujaibanerji/PM-Mass-and-AOPs-at-SMEAR-II/releases/tag/binder-20261026-absorption-and-mac-520).

The default run redraws Figures 2-8 and S1-S3 from frozen processed inputs,
preserves Figure 1 artwork, and recalculates dust-overlap diagnostics. Saved
bootstrap intervals are retained. It does not rerun the complete instrument-data
analysis or the additional sensitivity analyses. Their scripts and results are
included in the complete manuscript package.

For local use, extract binder.zip into binder/ beside data.zip and codes.zip,
install the pinned requirements in .binder/, then run:

```sh
python binder/launcher.py --archive-dir . --offline --output-dir results/new-run
```

See README_Previous_Release.md for historical documentation.
