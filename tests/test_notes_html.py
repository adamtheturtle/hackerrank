"""Read-back normalization accepts formatting and rejects changed
notes.
"""

import pytest

from hackerrank._notes_html import notes_equal


@pytest.mark.parametrize(
    argnames=("expected", "actual"),
    argvalues=[
        ("", ""),
        ("Plain text", "Plain text"),
        (
            "<p>Driver&#8217;s rate &#215; 2</p>",
            "<p>Driver\u2019s rate \u00d7 2</p>",
        ),
        (
            '<a href="/guide" class="link">Guide</a>',
            '<a class="link" href="/guide">Guide</a>',
        ),
        (
            (
                '<table><colgroup><col style="width: 50.0%"/></colgroup>'
                "<tbody><tr><td><p>Rate</p></td></tr></tbody></table>"
            ),
            (
                "<table>\n<colgroup>\n"
                '<col style="width:50.0%;">\n</colgroup>\n'
                "<tbody>\n<tr>\n<td><p>Rate</p></td>\n</tr>\n</tbody>\n</table>"
            ),
        ),
        (
            '<p style="color: red !important; width: 50%">Rate</p>',
            '<p style="color:red!important;width:50%;">Rate</p>',
        ),
        ('<p style="">Rate</p>', '<p style=";">Rate</p>'),
        (
            (
                "<div><p>Example</p>"
                "<pre><code>  x &lt; 3\n\tprint(x)\n</code></pre></div>"
            ),
            (
                "<div>\n<p>Example</p>\n"
                "<pre><code>  x &lt; 3\n\tprint(x)\n</code></pre>\n</div>"
            ),
        ),
    ],
)
def test_equivalent_notes(*, expected: str, actual: str) -> None:
    """Entity spelling, CSS separators, and block indentation may
    change.
    """
    assert notes_equal(expected=expected, actual=actual)


@pytest.mark.parametrize(
    argnames=("expected", "actual"),
    argvalues=[
        ("Notes", ""),
        ("<div>&nbsp;<p>Task</p></div>", "<div><p>Task</p></div>"),
        ("Notes\n", "Notes"),
        ("x &amp; y", "x & y"),
        ("<p>Required</p>", "<p>Changed</p>"),
        (
            "<details><summary>Prompt</summary><p>Task</p></details>",
            "<div><summary>Prompt</summary><p>Task</p></div>",
        ),
        ('<a href="/guide">Guide</a>', '<a href="/other">Guide</a>'),
        (
            '<img src="data:image/png;base64,abc"/>',
            '<img src="data:image/png;base64,def"/>',
        ),
        ('<p class="required">Task</p>', "<p>Task</p>"),
        ('<p style="color: red">Task</p>', '<p style="color: blue">Task</p>'),
        (
            '<p style="color: red !important">Task</p>',
            '<p style="color:red">Task</p>',
        ),
        (
            '<p style="color:red; color:blue">Task</p>',
            '<p style="color:blue; color:red">Task</p>',
        ),
        (
            "<p style=\"--label: 'a; b: c'\">Task</p>",
            "<p style=\"--label: 'a;b:c'\">Task</p>",
        ),
        ('<p style="invalid">Task</p>', '<p style="invalid;">Task</p>'),
        (
            '<p style="/* keep */ color:red">Task</p>',
            '<p style="color:red">Task</p>',
        ),
        (
            "<style>p { color: red }</style>",
            "<style>p { color: blue }</style>",
        ),
        ("<script>run()</script>", "run()"),
        ("<div><!-- keep --><p>Task</p></div>", "<div><p>Task</p></div>"),
        (
            "<p><span>A</span> <span>B</span></p>",
            "<p><span>A</span><span>B</span></p>",
        ),
        ("<pre>  x\n\ty\n</pre>", "<pre>x\ny\n</pre>"),
        ("<pre> </pre>", "<pre></pre>"),
        ("<code> </code>", "<code></code>"),
        ("<textarea> </textarea>", "<textarea></textarea>"),
        ("<div><p>Task</p></div>", "<div><p>Task</p><p>Extra</p></div>"),
    ],
)
def test_changed_notes(*, expected: str, actual: str) -> None:
    """Content, inline gaps, code whitespace, and attributes stay
    exact.
    """
    assert not notes_equal(expected=expected, actual=actual)
