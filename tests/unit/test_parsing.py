from siemens_wiki_common.parsing import parse_confluence_storage


def test_empty_input_returns_empty_string():
    assert parse_confluence_storage("") == ""


def test_strips_basic_tags_and_collapses_whitespace():
    html_ = "<p>Hello   world.</p>\n<h2>Section</h2>"
    assert parse_confluence_storage(html_) == "Hello world. Section"


def test_unwraps_structured_macro_keeping_text():
    html_ = (
        '<ac:structured-macro ac:name="info">'
        "<ac:rich-text-body><p>Info box content</p></ac:rich-text-body>"
        "</ac:structured-macro>"
    )
    assert parse_confluence_storage(html_) == "Info box content"


def test_removes_macro_parameters_and_plain_text_body():
    html_ = (
        '<ac:structured-macro ac:name="code">'
        '<ac:parameter ac:name="language">python</ac:parameter>'
        "<ac:plain-text-body>print(1)</ac:plain-text-body>"
        "</ac:structured-macro>"
        "<p>after</p>"
    )
    assert parse_confluence_storage(html_) == "after"


def test_decodes_html_entities():
    html_ = "<p>A &amp; B &lt;tag&gt;</p>"
    assert parse_confluence_storage(html_) == "A & B <tag>"
