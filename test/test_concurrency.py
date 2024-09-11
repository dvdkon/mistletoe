import unittest

from textwrap import dedent
from threading import Thread

from mistletoe import Document
from mistletoe.markdown_renderer import MarkdownRenderer

class TestConcurrency(unittest.TestCase):
    def test_ten_markdown_renderers(self):
        source = dedent("""\
        # This
        is *some* *Markdown* *document*!
        """)
        exception = None
        def thread():
            try:
                for i in range(1_000):
                    with MarkdownRenderer() as renderer:
                        doc = Document(source)
                        roundtrip = renderer.render(doc)
                        self.assertEqual(roundtrip, source)
            except Exception as e:
                nonlocal exception
                exception = e
        threads = [Thread(target=thread) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if exception is not None:
            raise exception
