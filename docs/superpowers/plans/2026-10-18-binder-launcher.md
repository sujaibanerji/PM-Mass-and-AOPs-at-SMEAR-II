# Hyytiälä Binder Launcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a locally verified Binder launcher that presents every distinct scientific figure, excludes redundant versions, and supports the existing full Python analysis.

**Architecture:** Audit the wider source project before fixing the final gallery inventory. Preserve the original code/data ZIPs and package distinct additional figures separately. Binder prepares the three verified archives at build time; a guided notebook renders the current figures, presents the complete gallery with provenance, and offers an explicit full-analysis action.

**Tech Stack:** Python 3.12.14, standard-library archive/network/filesystem tools, the original 16 pinned scientific packages, Jupyter supplied by repo2docker, Git, and WSL Ubuntu for Linux validation.

**Spec:** `docs/superpowers/specs/2026-10-18-binder-launcher-design.md` — user approved on 18 October 2026.

## Global Constraints

- Include every distinct scientific figure; exclude overlapping versions under the seven approved selection rules.
- Preserve the 17 registered package outputs: seven main-manuscript figures and ten supporting figures. The packaged SI has zero embedded figures.
- Keep `codes.zip` and `data.zip` unchanged. Their exact identities are in the spec; new artifacts are additive.
- Use Python 3.12.14 and the exact 16 pins from `codes.zip/python_codes/requirements.txt`; record the actual runtime.
- Preserve raw-versus-adjusted estimates, cohort differences, paired area/volume distributions, fixed artwork, saved-reference intervals, and historical scientific scope.
- An archived historical image is not a freshly calculated result. Register additional generation commands only with available portable inputs and successful validation.
- No heavy analysis starts from opening the notebook or running its normal introductory cells.
- Use fresh output directories, verify checksums, and never replace source observations or previous results.
- Keep local absolute paths, credentials, extracted archives, environments, and generated outputs out of the publishable Git repository.
- Public URLs may remain unset for local preparation. Network preparation must stop clearly when required URLs are unset.
- Linux evidence and actual MyBinder evidence are separate. Public creation/upload waits until concrete artifacts and archive destinations can be reviewed.

## Review Focus

1. Same-looking plots can have different wavelengths, cohorts, units, or processing: preserve scientific differences; test in Task 1.
2. Historical folders and vector-only figures can contain unique content: scan them and account for each candidate; test in Task 1.
3. Interrupted preparation can leave a partial destination: publish extraction only after validation and refuse unrelated destinations; test in Task 3.
4. Figures can share basenames across groups: gallery paths and downloads must retain both, with provenance; test in Task 4.
5. A notebook-wide Run All can accidentally launch a long calculation: require an independent explicit opt-in; test in Task 4.

---

## Files and responsibilities

| File | Responsibility |
| --- | --- |
| `tools/audit_figures.py` | Scan image candidates, fingerprints, source metadata, and resolved selection decisions. |
| `audit/selection_decisions.json` | Human-reviewed scientific overlap decisions using relative source identities. |
| `figure_inventory.json` | Canonical gallery entries, provenance, alternate placements/formats, and regeneration status. |
| `figure_exclusions.csv` | Every excluded candidate and its canonical replacement or artifact classification. |
| `tools/package_figures.py` | Build and verify the additive figure bundle from the resolved inventory. |
| `release_io.py` | Streaming integrity checks and safe staged archive preparation. |
| `prepare_release.py` | Local/network preparation CLI and original package-integrity check. |
| `binder_release.json` | Exact archive identities and eventual version-specific URLs. |
| `.binder/environment.yml` | Python 3.12.14 and pip for repo2docker. |
| `.binder/requirements.txt` | Exact original scientific pins. |
| `.binder/postBuild` | Install/check the pins, then prepare the configured release; stop on failure. |
| `reviewer.py` | Current rendering, gallery assembly, optional production commands, and downloads. |
| `Start_here.ipynb` | Guided reviewer workflow using `reviewer.py`. |
| `tests/test_*.py` | Focused failure, integrity, completeness, and opt-in tests. |
| `README.md` | Reviewer and author instructions plus the exact tested delivery status. |

Large bundles and local reports go under ignored `outputs/` and `work/`. Public provenance uses relative project identities; the local source-root mapping stays in `work/`.

### Task 1: Resolve the complete figure inventory

**Files:** Create `tools/audit_figures.py`, `audit/selection_decisions.json`, `figure_inventory.json`, `figure_exclusions.csv`, `tests/test_figure_audit.py`, and `.gitignore`.

**Interfaces:**
- `scan_sources(source_root: Path, baseline_root: Path) -> list[dict]`: candidates with stable IDs, relative source identity, format, byte hash, dimensions/pixel hash where applicable, and available caption/script/manifest references.
- `resolve_inventory(candidates: list[dict], decisions: dict) -> dict`: canonical `figures`, per-source `decisions`, and `unresolved` IDs. Publication requires an empty unresolved list.
- Each figure records `id`, `title`, `group`, `status`, `canonical_source`, `sha256`, `formats`, `placements`, `scope`, `provenance`, and `regeneration` (`registered` or `archived_image`).
- An exclusion records `source_id`, `reason`, `canonical_ids` (a list), and `evidence`. The list can name several retained figures when a redundant composite or figure book is fully covered by them. Only a non-scientific artifact may have no canonical replacement. Source-page identities are retained for figures found in PDF containers.

- [x] **Step 1: Write failing tests** named `test_same_basename_different_wavelengths_are_preserved`, `test_history_and_vector_only_candidates_are_scanned`, `test_identical_copy_has_canonical_replacement`, and `test_unresolved_or_missing_replacement_stops_finalization`. Use two same-named fixtures with `sca450` and `sca700`; assert both remain. Put a unique SVG under `history/`; assert it is indexed. Assert duplicate decisions name a retained ID and unresolved decisions prevent finalization.
- [x] **Step 2: Run** `python -m unittest discover -s tests -p test_figure_audit.py -v`; verify failure for the absent implementation.
- [x] **Step 3: Implement** the scan and decision validation interfaces. Index PNG/JPEG/TIFF/SVG/PDF scientific candidates across the approved source root, including history. Inspect PDF or SVG-only candidates using the appropriate document/figure tools. Never discard a scientific candidate solely on a perceptual similarity score or basename.
- [x] **Step 4: Audit the actual sources.** Use the prior PNG index as a starting reference, not the final candidate set. Prefer the verified current 17 images. Compare other images, captions, generating code, input/cohort identities, and composite panels; record explicit overlap decisions. Keep distinct historical results with their original conventions. Resolve every candidate, including QA/mockup/document-page artifacts. Do not claim an exact final figure count before this audit is finished.
- [x] **Step 5: Rerun tests and validate the actual inventory:** all 17 baseline entries present, all candidates accounted for, no unresolved IDs, and every excluded scientific copy linked to a retained replacement. Initialize local Git here, ignore `work/`, `outputs/`, environments and extracted data, then commit the reviewed docs and inventory deliverable.

### Task 2: Build the additional figure bundle

**Files:** Create `tools/package_figures.py`, `tests/test_figure_bundle.py`; generate ignored `outputs/additional_figures.zip`.

**Interfaces:**
- Consumes Task 1's resolved inventory and local source-root mapping.
- `build_bundle(inventory_path: Path, source_root: Path, output_zip: Path) -> dict`: returns the bundle's byte size, SHA-256, figure count and manifest identity.
- Bundle layout: `manifest.json`, `figures/<id>/<original-name>`, useful alternate formats, and provenance/caption records. Every member has a checksum. Figure IDs prevent basename collisions. The manifest distinguishes archived images from validated generation registrations.

- [x] **Step 1: Write failing tests** `test_two_groups_with_same_filename_both_survive`, `test_bundle_bytes_match_sources`, and `test_public_manifest_contains_no_absolute_local_paths`. Assert two `figure_1.png` fixtures have distinct members, extracted bytes equal the originals, and local source roots do not appear in the manifest.
- [x] **Step 2: Run** `python -m unittest discover -s tests -p test_figure_bundle.py -v`; confirm the expected missing-implementation failures.
- [x] **Step 3: Implement** deterministic packaging of the retained additional figures. Preserve original image bytes. Capture source-code/input identities; include an executable regeneration registration only after its command, compatible inputs, and validation are established. An unavailable historical pipeline remains explicitly `archived_image`.
- [x] **Step 4: Run tests, build the actual bundle, extract it to a fresh temporary directory, and byte-compare every member with its source.** Rehash the two original ZIPs and confirm the spec identities remain unchanged. Commit packaging code, tests, and public inventory metadata; leave the bundle ignored.

### Task 3: Prepare the matching release locally and in Binder

**Files:** Create `release_io.py`, `prepare_release.py`, `binder_release.json`, `.binder/environment.yml`, `.binder/requirements.txt`, `.binder/postBuild`, and `tests/test_release_io.py`.

**Interfaces:**
- `prepare_release(config: Path, destination: Path, local_archives: dict[str, Path] | None = None) -> dict`: returns validated paths for `codes`, `data`, and `additional_figures`, plus archive identities.
- CLI: `python prepare_release.py --config binder_release.json --destination runtime [--codes-zip PATH --data-zip PATH --figures-zip PATH]`. Local mode requires all three overrides; network mode requires all three version-specific HTTPS URLs.
- Config has a release ID and an `archives` mapping for `codes`, `data`, `additional_figures`, each with `filename`, `bytes`, `sha256`, and `url`. Unset URLs are intentional local-only configuration, not guessed public links.

- [x] **Step 1: Write failing tests** for a corrupted archive, a failed download, a ZIP path escaping the staging directory, missing network URLs, an unrelated existing destination, and successful reuse of the same validated release. Assert failures leave sources unchanged and do not expose a partial prepared destination.
- [x] **Step 2: Run** `python -m unittest discover -s tests -p test_release_io.py -v`; verify the absent implementation is the failure cause.
- [x] **Step 3: Implement** streaming download/hash checks, staged extraction, and final validation. Verify byte size and SHA-256 before extraction; reject escaping paths and link entries. Extract the original rootless archives into sibling directories. Run their original `package_checks.py` against the data directory; verify the additive bundle manifest. Publish the prepared destination only after every check passes.
- [x] **Step 4: Configure Binder.** Pin Python 3.12.14 in `environment.yml`. Copy the original requirements exactly. `postBuild` uses `set -eu`, installs those requirements through the selected Python, runs `pip check`, and calls the preparation CLI in network mode. Test script execution in Linux; it must stop when URLs are unset. Record the actual runtime rather than inferring it from configuration.
- [x] **Step 5: Run the failure tests and a real local preparation using the three archives in a destination containing spaces.** Confirm the source hashes remain unchanged and commit this preparation deliverable.

### Task 4: Add the complete reviewer notebook and downloads

**Files:** Create `reviewer.py`, `Start_here.ipynb`, and `tests/test_reviewer.py`.

**Interfaces:**
- Consumes Task 3's prepared-release paths and Task 1's inventory.
- `render_saved(prepared: dict, output: Path) -> dict`: renders seven main figures and ten supporting figures from the original saved inputs, verifies the extra archived assets, and returns a complete gallery manifest with estimate origins.
- `run_full(prepared: dict, output: Path, *, confirmed: bool = False) -> dict`: refuses without explicit confirmation, invokes registered production commands in a fresh `output/analysis` directory, assembles the complete gallery in `output/gallery`, and returns validated job/figure outcomes. Do not prepopulate the analysis directory before the original launcher reserves it.
- `build_gallery(manifest: dict, output: Path) -> Path` and `export_results(manifest: dict, output_zip: Path) -> Path`: serve every selected image under its stable ID and retain captions, provenance, and regeneration status.

- [x] **Step 1: Write failing tests** proving same-named images from different groups survive gallery/export, missing expected images stop completion, saved intervals are labelled `saved_reference`, archived historical figures stay labelled `archived_image`, captions are safely displayed, and `run_full(..., confirmed=False)` launches no subprocess.
- [x] **Step 2: Run** `python -m unittest discover -s tests -p test_reviewer.py -v`; verify the expected failures.
- [x] **Step 3: Implement** the helper interfaces with fresh output directories. Use the original `figure_renderer.render` for Figures 1–7 and `supporting_plots.render_supporting` with `data/reference` for the ten saved-input supporting plots. Keep the inherited manifests and add explicit estimate-origin records. Build a gallery that loads images as files rather than embedding all full-resolution images into notebook memory. Offer individual files, useful alternate formats, and one complete result ZIP.
- [x] **Step 4: Implement the notebook.** Explain scope, verify the prepared inputs, render/view the entire inventory, and offer downloads. Place production execution in a separate cell guarded by `RUN_FULL_ANALYSIS = False`; Run All must skip the heavy workflow. The opt-in command uses `run_all.py --language python --all-methods --size-bootstrap --native-size-bootstrap`, preserving default 5000/2000 draws and the original reference check. Show live job/log progress. Never present archived historical images as newly recomputed outputs.
- [x] **Step 5: Run tests and execute the normal notebook path with a notebook runner.** Assert the production guard remains false and no production job directory is created. Verify every selected figure has a gallery entry and download member. Commit the notebook deliverable.

### Task 5: Validate on Linux and inspect every retained figure

**Files:** Create `tools/validate_linux.py`; save logs, executed notebook, visual-review records, and runtime reports under ignored `work/linux_validation/`.

**Interfaces:** Consumes all previous deliverables. Produces a validation report containing actual runtime/package versions, source hashes, commands, exit codes, timings, peak memory where available, inventory counts, image checks, and explicit untested environments.

- [x] **Step 1: Create a separate Python 3.12.14 environment inside WSL Ubuntu** using a user-scoped runtime installer; do not replace Ubuntu's Python 3.12.3. Keep bootstrap tools separate from product requirements. Verify `python --version`, install the exact requirements and notebook-runner tools in the appropriate environments, and run `pip check`.
- [x] **Step 2: Run all focused tests and prepare the real release on Linux.** Execute the normal notebook path with the full selected inventory. Record elapsed time and peak resident memory using `/usr/bin/time -v` when available.
- [x] **Step 3: Inspect every retained image**, with contact sheets for navigation and full-resolution checks as needed. Confirm that overlap decisions preserve different scientific content, all images are readable, and historical backscatter/geometry conventions are labelled. Check gallery entries, alternate placements, source hashes, and the complete download. Fix actual defects and rerun only affected checks.
- [x] **Step 4: Run the full current Python production workflow once on Linux.** Retain all logs and numerical reference verification. Verify seven current main figures and ten supporting figures; inspect any image differences from Windows without silently weakening scientific checks. Validate each added generation registration separately. Record resource/runtime failures honestly if completion is prevented.
- [x] **Step 5: Rehash protected sources, reconcile the complete inventory and exclusions, and record the precise Linux acceptance result.** A successful WSL run does not count as an actual Binder build. Commit validation tooling and concise public status documentation, without local logs or scientific assets.

### Task 6: Package the local handoff and prepare the online launch

**Files:** Create `README.md`, `tools/package_launcher.py`, and ignored `outputs/Binder_launcher_local_20261018.zip`; retain `outputs/additional_figures.zip` separately.

**Interfaces:** Consumes the verified local launcher, resolved figure inventory, original archive identities, and validation report. Produces the launcher ZIP, additive figure ZIP, artifact checksums, and a concrete publication checklist containing the three needed archive URLs and proposed public repository destination.

- [x] **Step 1: Write concise reviewer/author instructions.** Explain all-figure coverage, duplicate selection, saved-input versus production calculation, historical-image status, result downloads, tested Linux scope, and the remaining actual MyBinder test. Document local commands without machine-specific paths. Include the original two archive hashes and the new artifact identities.
- [x] **Step 2: Package an explicit allowlist of launcher files.** Exclude `.git`, source archives, environments, local paths/configuration, caches, and generated data/results. Extract to a new directory containing spaces and verify the packaged preparation/notebook workflow with explicit local archive paths. Test archive members and byte identities rather than assuming the ZIP is complete.
- [x] **Step 3: Obtain one independent final review of the implementation and scientific-inventory decisions.** Use the chosen execution workflow's review mechanism, resolve verified findings, and run the relevant final checks before claiming completion.
- [x] **Step 4: Present the concrete local artifacts and proposed public file/repository changes.** Resolve the version-specific archive URLs and destination before public creation/upload. Then pin the Binder link to an immutable commit, run an actual Binder build and full-gallery notebook test, and record that online result separately. If publication inputs or approval remain outstanding, deliver the verified local artifacts and state precisely what the public launch still requires.

## Plan self-review

- Spec coverage: Tasks 1–2 cover all-image selection and source preservation; Task 3 covers matching archive preparation and Binder configuration; Task 4 covers notebook behavior and downloads; Task 5 covers Linux/scientific/visual validation; Task 6 covers reproducible delivery and online acceptance.
- Interface consistency: inventory, bundle, preparation, and gallery functions above are the interfaces subsequent tasks consume. Archive visibility and regeneration status stay explicit throughout.
- Review focus: all five listed failure classes have targeted tests in their owning tasks.
- No final figure count is assumed beyond the required 17 baseline outputs; the complete count is produced by the resolved wider audit.
- Native implementation and the local acceptance steps are complete. The independently reviewed handoff contains 192 figures and 396 assets. Public publication approval, version-specific URLs and an actual MyBinder build remain the next stage; no public launch is claimed.
