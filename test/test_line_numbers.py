import unittest

from mistletoe import block_token, span_token
from mistletoe.parser import Parser
from mistletoe.markdown_renderer import (
    LinkReferenceDefinition,
    LinkReferenceDefinitionBlock,
)


class TestLineNumbers(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = Parser()
        self.parser.add_block_token(block_token.HTMLBlock)
        self.parser.add_span_token(span_token.HTMLSpan)
        self.parser.remove_block_token(block_token.Footnote)
        self.parser.add_block_token(LinkReferenceDefinitionBlock)
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_main(self):
        # see line_numbers.md for a description of how the test works.
        NUMBER_OF_LINE_NUMBERS_TO_BE_CHECKED = 13
        with open("test/samples/line_numbers.md", "r") as fin:
            document = self.parser.parse_document(fin)
        count = self.check_line_numbers(document)
        self.assertEqual(count, NUMBER_OF_LINE_NUMBERS_TO_BE_CHECKED)

    def check_line_numbers(self, token: block_token.BlockToken):
        """Check the line number on the given block token and its children, if possible."""
        count = 0
        line_number = self.get_expected_line_number(token)
        if line_number:
            self.assertEqual(token.line_number, line_number)
            count += 1

        if isinstance(token, block_token.Table):
            count += self.check_line_numbers(token.header)

        for child in token.children:
            if isinstance(child, block_token.BlockToken):
                count += self.check_line_numbers(child)

        return count

    def get_expected_line_number(self, token: block_token.BlockToken):
        # the expected line number, if it exists, should be wrapped in an inline
        # code token and be an immediate child of the token.
        # or it could be the title of a link reference definition.
        for child in token.children:
            if isinstance(child, span_token.InlineCode):
                return int(child.children[0].content)
            if isinstance(child, LinkReferenceDefinition):
                return int(child.title)
