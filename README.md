# SMEAR II manuscript and supplementary figure reproduction

## Current verified release: absorption and MAC at 520 nm

[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://gesis.mybinder.org/v2/gh/sujaibanerji/PM-Mass-and-AOPs-at-SMEAR-II/ff218d82cecbc95833df982759320d6c58453bb3?urlpath=voila/render/One_click.ipynb)

**[Open the verified automatic-start Binder](https://gesis.mybinder.org/v2/gh/sujaibanerji/PM-Mass-and-AOPs-at-SMEAR-II/ff218d82cecbc95833df982759320d6c58453bb3?urlpath=voila/render/One_click.ipynb).** Keep the tab open; the
figures and the results ZIP download appear automatically. Download your results
before closing Binder because session storage is temporary.

The revised quantities are $\sigma_{\mathrm{abs},520}$ and
$\mathrm{MAC}_{520}$. Scattering, MSC and SSA remain at 550 nm; SSA uses
absorption matched to 550 nm. The current figures include the revised numeric
formatting, collection counts and Figure 6 calendar display.

The [matching release](https://github.com/sujaibanerji/PM-Mass-and-AOPs-at-SMEAR-II/releases/tag/binder-20261026-520-verified) provides
`data.zip`, `codes.zip`, `binder.zip` and the hosted verification receipt.
The Binder link is pinned to
[`ff218d82cecbc95833df982759320d6c58453bb3`](https://github.com/sujaibanerji/PM-Mass-and-AOPs-at-SMEAR-II/tree/ff218d82cecbc95833df982759320d6c58453bb3); archive sizes and SHA-256 hashes
are fixed in [binder_release.json](binder_release.json).

**Hosted verification passed on GESIS Binder on 26 October 2026.** The automatic
Voila run downloaded and verified the revised archives, completed all four jobs,
and reproduced all 11 figures with pixels identical to the delivered references.
The downloadable results ZIP also passed its integrity check. The receipt is
[HOSTED_VERIFICATION.json](HOSTED_VERIFICATION.json).

The code audit's two integrity findings are fixed. The final advisory scan of all
145 installed Python packages reported no known vulnerabilities. See
[SECURITY-AUDIT.json](SECURITY-AUDIT.json) for the scope and remaining limits.

The default run redraws Figures 2-8 and S1-S3 from frozen processed inputs,
preserves Figure 1 artwork, and recalculates dust-overlap diagnostics. Saved
bootstrap intervals are retained. It does not rerun the complete instrument-data
analysis or the additional sensitivity analyses. Their scripts and results are
included in the complete manuscript package. Optional historical r6 recomputation
is separate and is not part of this hosted acceptance test.

## Local use

Extract binder.zip into binder/ beside data.zip and codes.zip. Install the pinned
requirements in .binder/, then run:

```sh
python binder/launcher.py --archive-dir . --offline --output-dir results/new-run
```

The archive `release_id` is a historical internal schema identifier;
`local_revision` and `release_tag` identify the current 520 nm release.
See README_Previous_Release.md and HOSTED-VERIFICATION-PREVIOUS.json for history.
