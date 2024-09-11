from typing import Any, TYPE_CHECKING

from mistletoe import token, block_token, span_token, block_tokenizer, span_tokenizer

if TYPE_CHECKING:
    from mistletoe.block_token import Document

class Parser:
    """
    Parser context class containing e.g. list of possible block and span tokens.
    """

    _block_token_types: list[type[token.Token]]
    _span_token_types: list[type[token.Token]]
    _fallback_token: type[token.Token]
    _root_node: "Document | None"
    context: dict[str, Any]
    """
    Stores a reference to the current document (root) token during parsing.

    Footnotes are stored in the document token by accessing this reference.
    """

    def __init__(self):
        self._block_token_types = []
        self._span_token_types = []
        self._root_node = None
        self.context = {}
        self.reset_tokens()

    def parse_document(self, lines):
        if isinstance(lines, str):
            lines = lines.splitlines(keepends=True)
        lines = [line if line.endswith('\n') else '{}\n'.format(line) for line in lines]
        doc = block_token.Document()
        self._root_node = doc
        doc.children = self.tokenize_blocks(lines)
        self._root_node = None
        return doc

    def tokenize_blocks(self, lines):
        """
        A wrapper around block_tokenizer.tokenize. Pass in all block-level
        token constructors as arguments to block_tokenizer.tokenize.

        Doing so (instead of importing block_token module in block_tokenizer)
        avoids cyclic dependency issues, and allows for future injections of
        custom token classes.

        _token_types variable is at the bottom of this module.

        See also: block_tokenizer.tokenize, span_token.tokenize_inner.
        """
        return block_tokenizer.tokenize(lines, self, self._block_token_types)

    def add_block_token(self, token_cls, position=0):
        """
        Allows external manipulation of the parsing process.
        This function is usually called in BaseRenderer.__enter__.

        Arguments:
            token_cls (SpanToken): token to be included in the parsing process.
            position (int): the position for the token class to be inserted into.
        """
        self._block_token_types.insert(position, token_cls)

    def remove_block_token(self, token_cls):
        """
        Allows external manipulation of the parsing process.
        This function is usually called in BaseRenderer.__exit__.

        Arguments:
            token_cls (BlockToken): token to be removed from the parsing process.
        """
        self._block_token_types.remove(token_cls)

    def tokenize_inner(self, content):
        """
        A wrapper around span_tokenizer.tokenize. Pass in all span-level token
        constructors as arguments to span_tokenizer.tokenize.

        Doing so (instead of importing span_token module in span_tokenizer)
        avoids cyclic dependency issues, and allows for future injections of
        custom token classes.

        See also: span_tokenizer.tokenize, tokenize_blocks.
        """
        return span_tokenizer.tokenize(
            self, content, self._span_token_types, self._fallback_token
        )

    def add_span_token(self, token_cls, position=1):
        """
        Allows external manipulation of the parsing process.
        This function is called in BaseRenderer.__enter__.

        Arguments:
            token_cls (SpanToken): token to be included in the parsing process.
        """
        self._span_token_types.insert(position, token_cls)


    def remove_span_token(self, token_cls):
        """
        Allows external manipulation of the parsing process.
        This function is called in BaseRenderer.__exit__.

        Arguments:
            token_cls (SpanToken): token to be removed from the parsing process.
        """
        self._span_token_types.remove(token_cls)

    def reset_tokens(self):
        """
        Resets _*_token_types to all token classes in block_token and span_token module.
        """
        for i, cls_name in enumerate(block_token.__all__):
            self.add_block_token(getattr(block_token, cls_name), i)
        for i, cls_name in enumerate(span_token.__all__):
            if cls_name == "SpanToken":
                continue
            self.add_span_token(getattr(span_token, cls_name), i)
        self._fallback_token = span_token.RawText


_global_parser: Parser | None = None
"""Global parser set by renderer for API compatibility"""
