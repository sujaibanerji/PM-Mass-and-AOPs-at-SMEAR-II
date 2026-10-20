"""The UI worker must inherit the calling notebook's execution context."""
from contextvars import ContextVar
from threading import Event
from unittest.mock import patch
import unittest
import test_one_click as contracts


class WorkerContextTests(unittest.TestCase):
    setUp = contracts.AutoStartTests.setUp
    def test_real_worker_inherits_notebook_context(self):
        from threading import Thread
        marker = ContextVar('notebook_execution_context', default='missing')
        marker.set('current-notebook')
        completed = Event()
        observed = []

        def runner(**kwargs):
            observed.append(marker.get())
            completed.set()
            return self.result

        with patch.object(self.ui, 'Thread', Thread), patch.object(self.ui, 'run', runner):
            self.ui.show()
            self.assertTrue(completed.wait(5), 'Worker did not run')
        self.assertEqual(observed, ['current-notebook'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
