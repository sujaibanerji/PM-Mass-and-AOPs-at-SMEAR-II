import json
import tempfile
import unittest
from pathlib import Path

try:
    from tools.audit_figures import resolve_inventory, scan_sources
except ImportError:
    resolve_inventory = scan_sources = None


class FigureAuditTests(unittest.TestCase):
    def test_author_excluded_scientific_figure_needs_no_retained_replacement(self):
        rows = [dict(source_id='retained', relative='mass.png', sha256='a'),
                dict(source_id='excluded', relative='coefficient.png', sha256='b')]
        decisions = {
            'retained': dict(decision='keep', id='mass', title='Mass', group='mass'),
            'excluded': dict(decision='out_of_scope', canonical_ids=[],
                             evidence='Author explicitly removed this measurement from delivery')}
        try:
            result = resolve_inventory(rows, decisions)
        except ValueError as error:
            self.fail(f'Explicit scope exclusion should resolve without a replacement: {error}')
        self.assertEqual([f['id'] for f in result['figures']], ['mass'])
        self.assertEqual(result['decisions'][1]['canonical_ids'], [])

    def test_scope_exclusion_requires_documented_evidence(self):
        row = dict(source_id='a', relative='a.png', sha256='a')
        with self.assertRaises(ValueError):
            resolve_inventory([row], {'a': dict(decision='out_of_scope', canonical_ids=[])})

    def test_reviewed_inventory_preserves_changed_mass_selection_cohorts(self):
        inventory = json.loads((Path(__file__).resolve().parents[1] / 'figure_inventory.json').read_text(encoding='utf-8'))
        selected = [f for f in inventory['figures'] if f['canonical_source'].endswith(
            ('/categories_all_channels_mass.png', '/categories_scattering_mass.png'))]
        self.assertEqual(len(selected), 4, 'Preserve the four distinct historical mass-selection cohorts')

    def test_historical_sphere_surface_composite_is_distinct_from_projected_area(self):
        inventory = json.loads((Path(__file__).resolve().parents[1] / 'figure_inventory.json').read_text(encoding='utf-8'))
        selected = [f for f in inventory['figures'] if f['canonical_source'].endswith('/FOUR_CATEGORY_DISTRIBUTIONS.png')]
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['regeneration'], 'archived_image')
        self.assertIn('sphere', selected[0]['title'].lower())

    def test_history_and_vector_only_candidates_are_scanned(self):
        self.assertIsNotNone(scan_sources, "The complete source scanner is missing")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "history").mkdir()
            (root / "history/unique.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            rows = scan_sources(root, None)
            self.assertEqual([r["relative"] for r in rows], ["history/unique.svg"])

    def test_same_basename_different_wavelengths_are_preserved(self):
        self.assertIsNotNone(resolve_inventory, "Scientific selection resolver is missing")
        candidates = [dict(source_id="a", relative="450/plot.png", sha256="1"),
                      dict(source_id="b", relative="700/plot.png", sha256="2")]
        decisions = {"a": dict(decision="keep", id="sca450", title="450 nm", group="optics"),
                     "b": dict(decision="keep", id="sca700", title="700 nm", group="optics")}
        result = resolve_inventory(candidates, decisions)
        self.assertEqual([f["id"] for f in result["figures"]], ["sca450", "sca700"])

    def test_identical_copy_has_canonical_replacement(self):
        self.assertIsNotNone(resolve_inventory, "Scientific selection resolver is missing")
        rows = [dict(source_id="a", relative="a.png", sha256="same"),
                dict(source_id="b", relative="b.png", sha256="same")]
        decisions = {"a": dict(decision="keep", id="one", title="One", group="optics"),
                     "b": dict(decision="duplicate", canonical_ids=["one"], evidence="Identical hash")}
        result = resolve_inventory(rows, decisions)
        self.assertEqual(len(result["figures"]), 1)
        self.assertEqual(result["decisions"][1]["canonical_ids"], ["one"])

    def test_unresolved_or_missing_replacement_stops_finalization(self):
        self.assertIsNotNone(resolve_inventory, "Scientific selection resolver is missing")
        row = dict(source_id="a", relative="a.png", sha256="a")
        with self.assertRaises(ValueError):
            resolve_inventory([row], {})
        with self.assertRaises(ValueError):
            resolve_inventory([row], {"a": dict(decision="duplicate", canonical_ids=["missing"])})


if __name__ == "__main__":
    unittest.main()
