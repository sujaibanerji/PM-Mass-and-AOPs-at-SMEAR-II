# Current manuscript and reproducibility-package reconciliation

The author requested autonomous continuation after moving pollen grains per gram
to the main manuscript. The present manuscript has eight main figures and no SI
figures. Earlier seven-figure acceptance remains a preserved historical release.
The author's subsequent scope decisions supersede the original plan's counts.

Native implementation, followed by one independent final review:

- [x] Add a tested ratio calculation using actual collection boundaries, full
  pollen coverage and finite nonnegative PM10 plus super-PM10 masses. Keep zeros;
  exclude incomplete coverage and invalid denominators; never add nested masses.
- [x] Generate Figure 6 and its full-precision table in the existing production
  workflow. Renumber size distributions to 7 and uncertainty to 8. Preserve the
  exact flowchart and all previously verified numerical estimates.
- [x] Update figure inventory and release manifests. Preserve old versions and
  make an additive public release; do not publish private repository history.
- [x] Run relevant complete test suites and a fresh actual MyBinder one-button
  production run with standard production settings; inspect the new plot,
  gallery, downloadable results, provenance and references.
- [x] Refresh the two Zenodo upload directories, copy-paste metadata and checksums.
  Keep current manuscripts separately because prose licensing was not granted.
- [x] Obtain one independent final review, resolve material findings, and deliver
  current manuscript/SI, ZIPs and immutable Binder launch link.

The OLS calibration remains (AE33 - 0.16) / 2.33 followed by STP conversion.
Its independently replicated Figure S9 result does not justify a numerical
recalibration. Frozen historical reports retain their original scope/date.
