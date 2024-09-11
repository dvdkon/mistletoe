from unittest import TestCase, mock
from mistletoe import span_token, Document
from mistletoe.parser import Parser
from mistletoe.contrib.github_wiki import GithubWiki, GithubWikiRenderer


class TestGithubWiki(TestCase):
    def setUp(self):
        self.renderer = GithubWikiRenderer()
        self.renderer.parser._root_node = Document([])
        self.renderer.__enter__()
        self.addCleanup(self.renderer.__exit__, None, None, None)

    def test_parse(self):
        MockRawText = mock.Mock()
        self.renderer.parser._fallback_token = MockRawText
        tokens = self.renderer.parser.tokenize_inner('text with [[wiki | target]]')
        token = tokens[1]
        self.assertIsInstance(token, GithubWiki)
        self.assertEqual(token.target, 'target')
        MockRawText.assert_has_calls([mock.call('text with '), mock.call('wiki')])

    def test_render(self):
        token = next(iter(self.renderer.parser.tokenize_inner('[[wiki|target]]')))
        output = '<a href="target">wiki</a>'
        self.assertEqual(self.renderer.render(token), output)
