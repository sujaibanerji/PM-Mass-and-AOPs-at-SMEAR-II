"""Actual HTTP coverage for the spinner caused by rejected Voilà JS/CSS."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from voila.static_file_handler import MultiStaticFileHandler, TemplateStaticFileHandler


class StaticAssetsTests(AsyncHTTPTestCase):
    def get_app(self):
        self.temp=tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.temp.cleanup)
        root=Path(self.temp.name)
        self.first=root/'first'; self.second=root/'second'
        self.first.mkdir(); self.second.mkdir()
        (self.second/'voila.js').write_text('window.fixtureLoaded=true;',encoding='utf-8')
        (self.second/'index.css').write_text('body { color: black; }',encoding='utf-8')
        (root/'private.txt').write_text('must not be served',encoding='utf-8')
        self.paths=patch('voila.static_file_handler.collect_static_paths',return_value=[str(self.second)])
        self.paths.start(); self.addCleanup(self.paths.stop)
        return Application([
            (r'/voila/static/(.*)',MultiStaticFileHandler,{'paths':[str(self.first),str(self.second)]}),
            (r'/voila/templates/(.*)',TemplateStaticFileHandler),
        ])

    def test_javascript_in_second_configured_static_root_is_served(self):
        response=self.fetch('/voila/static/voila.js')
        self.assertEqual(response.code,200)
        self.assertEqual(response.body,b'window.fixtureLoaded=true;')

    def test_template_stylesheet_is_served_from_its_real_root(self):
        response=self.fetch('/voila/templates/lab/static/index.css')
        self.assertEqual(response.code,200)
        self.assertEqual(response.body,b'body { color: black; }')

    def test_parent_traversal_remains_rejected(self):
        response=self.fetch('/voila/static/%2e%2e/private.txt')
        self.assertEqual(response.code,403)
        self.assertNotIn(b'must not be served',response.body)


if __name__=='__main__':unittest.main(verbosity=2)
