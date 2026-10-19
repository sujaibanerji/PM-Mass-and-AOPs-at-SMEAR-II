FIGURE S9 REPLICATION — Banerji et al. (2025)

The published relation is AE33₆₆₀ = 2.33 * MAAP₆₃₇ + 0.16, R² = 0.96.
OLS with a freely fitted intercept on 37,020 paired hourly medians gives:
slope 2.3315177741608997; intercept +0.1604597140968682 Mm⁻¹;
R² 0.9597021427180543. Independent NumPy least squares agrees.
The production inverse is (AE33 - 0.16) / 2.33, followed by STP scaling.
The rounded published constants are retained, so no production values change.

Use Python 3.12.14. Extract calibration_code.zip and
calibration_verification_data.zip into sibling code and data directories:

python -m pip install -r code/requirements.txt
python code/replicate_s9.py --paired-source data/paired_minute_observations.csv --output reproduced

The input CSV contains the exact UTC AE33/MAAP pairs before the historical
selection, not the complete original instrument files. MAAP values are XR_A21
equivalent black carbon multiplied by 6.6 m² g⁻¹; AE33 uses Ba5_A81 at 660 nm.
Original source hashes are in SOURCE_PROVENANCE.json. All ten originals can be
read instead using --project PATH_TO_ORIGINAL_PROJECT (with its abs folder).
The raw export input timestamps are UTC and receive no inter-instrument shift.

The authored recipe removes the single minimum AE value, then removes equal
value runs of at least 10 records in MAAP and then AE33. It retains both values
>= 0.05 Mm⁻¹ and strict two-sided ratios < 10, then forms paired hourly
medians in bins offset by 30 minutes. The historical mean-named plot reuses
the preceding median x/y variables. This delivery computes the median fit
explicitly and does not reuse plotting state. This recipe differs from the
later production hourly means, alternating-inlet selection and hourly QC.

Figure S9 displays a positive intercept. The article prose prints a negative
sign. The author requested the S9 relation; the correct inverse subtracts
0.16. The calibration directly compares 660 nm with 637 nm. Applying its
inherited adjustment to all seven AE channels is a separate assumption; the
replication does not establish independent calibration at every wavelength.

HOURLY_CORRECTION_AUDIT.json verifies all seven stored absorption channels in
both inlets, STP factors, hourly QC, the pre-2018 boundary, and equality with
the portable production input after aligning keys. 204,908 inlet-hours were
checked. The portable CSV is byte-identical to the completed production input.
It is a sorted/reserialized version of the earlier hourly cache. No numerical
change is required, so previous Python/Julia comparisons and the full online
production run remain applicable at their originally documented coverage.
Julia was not rerun for this documentation supplement.

audit_current_correction.py is a supplementary local audit, requiring the
upstream processing directory (not distributed in the portable input archive):
python code/audit_current_correction.py --pipeline PATH_TO_PIPELINE --data-zip data.zip --output audit.json

Reference:
https://acp.copernicus.org/articles/25/16895/2025/acp-25-16895-2025-supplement.pdf

The calibration dataset and additional source ZIP are prepared for the author-designated Zenodo data/code records. Public resolution may await publication. To reconstruct from local original exports now, run replicate_s9.py --project PATH --output reproduced.
