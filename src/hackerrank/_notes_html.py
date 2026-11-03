"""Compare note HTML while retaining content and meaningful whitespace."""

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from tinycss2 import parse_declaration_list, serialize
from tinycss2.ast import Declaration

_BLOCK_ELEMENTS = frozenset(
    {
        "article",
        "aside",
        "blockquote",
        "col",
        "colgroup",
        "dd",
        "details",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "summary",
        "table",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "tr",
        "ul",
    }
)
_LITERAL_ELEMENTS = frozenset({"pre", "code", "textarea", "script", "style"})


def _style(value: str, /) -> str:
    """Normalize declaration separators without rewriting CSS values."""
    declarations = parse_declaration_list(
        input=value, skip_comments=False, skip_whitespace=True
    )
    if not all(isinstance(item, Declaration) for item in declarations):
        return value
    return ";".join(
        item.name
        + ":"
        + serialize(nodes=item.value).strip(" \t\r\n\f")
        + ("!important" if item.important else "")
        for item in declarations
        if isinstance(item, Declaration)
    )


def _formatting_space(node: NavigableString, /) -> bool:
    """Ignore indentation next to block elements, retaining inline
    gaps.
    """
    if bool(str(object=node).strip(" \t\r\n\f")) or any(
        parent.name in _LITERAL_ELEMENTS for parent in node.parents
    ):
        return False
    return any(
        isinstance(sibling, Tag) and sibling.name in _BLOCK_ELEMENTS
        for sibling in (node.previous_sibling, node.next_sibling)
    )


def _normalized_html(value: str, /) -> str:
    """Normalize entity spelling, attributes, CSS, and block
    indentation.
    """
    soup = BeautifulSoup(markup=value, features="html.parser")
    if soup.find() is None:
        return value
    for tag in soup.find_all():
        style = tag.get(key="style")
        if isinstance(style, str):
            tag["style"] = _style(style)
    for node in list(soup.descendants):
        # Comments and other NavigableString subclasses are meaningful markup.
        if type(node) is NavigableString and _formatting_space(node):  # pylint: disable=unidiomatic-typecheck
            _ = node.extract()
    return soup.decode()


def notes_equal(*, expected: str, actual: str) -> bool:
    """Accept observed HTML formatting without ignoring lost content."""
    return expected == actual or _normalized_html(
        expected
    ) == _normalized_html(actual)
