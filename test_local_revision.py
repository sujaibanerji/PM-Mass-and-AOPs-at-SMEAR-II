"""Regression coverage for the current local release configuration."""
import unittest
from unittest.mock import patch
import test_one_click as contracts

class LocalRevisionTests(unittest.TestCase):
    setUp=contracts.AutoStartTests.setUp
    finish=contracts.AutoStartTests.finish
    def test_local_revision_with_null_release_tag_displays_and_starts(self):
        config={'release_id':'binder-20261025-count-explanations',
                'release_tag':None,'local_revision':'20261026-flag-555-lowercase'}
        with patch.object(self.ui,'configuration',lambda:config):
            view=self.ui.show()
        self.assertIn('20261026-flag-555-lowercase',' '.join(map(str,self.displayed)))
        self.finish()
        self.assertEqual(self.calls,[False])
        self.assertEqual(view.state,'succeeded')

    def test_hosted_release_tag_without_local_revision_still_works(self):
        config={'release_id':'binder-20261025-count-explanations','release_tag':'published-test'}
        with patch.object(self.ui,'configuration',lambda:config):
            self.ui.show()
        self.assertIn('published-test',' '.join(map(str,self.displayed)))

if __name__=='__main__':unittest.main(verbosity=2)
