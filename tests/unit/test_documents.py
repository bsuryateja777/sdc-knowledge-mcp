import json
from pathlib import Path

from siemens_wiki_common.documents import build_search_document
from siemens_wiki_common.models import ConfluencePage

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "shared" / "siemens_wiki_common" / "schema.json"


def _sample_page() -> ConfluencePage:
    return ConfluencePage(
        id="295931756",
        title="Siemens Data & AI Cloud",
        space_key="en",
        space_name="Global Wiki English",
        body_storage="<p>irrelevant here</p>",
        version_number=237,
        last_modified="2024-11-15T10:00:00.000Z",
        labels=["snowflake"],
        ancestors=["Global Wiki English Home"],
        source_url="https://wiki.siemens.com/spaces/en/pages/295931756/Siemens+Data+AI+Cloud",
    )


def test_build_search_document_id_and_chunk_index():
    doc = build_search_document(_sample_page(), "some chunk text", 2, [0.1, 0.2])
    assert doc.id == "295931756_chunk_2"
    assert doc.chunk_index == 2
    assert doc.content == "some chunk text"


def test_build_search_document_passes_through_source_url_verbatim():
    doc = build_search_document(_sample_page(), "chunk", 0, [0.1])
    assert doc.source_url == "https://wiki.siemens.com/spaces/en/pages/295931756/Siemens+Data+AI+Cloud"


def test_document_fields_match_schema_field_names():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    schema_fields = {f["name"] for f in schema["fields"]}

    doc = build_search_document(_sample_page(), "chunk", 0, [0.1])
    doc_fields = set(doc.__dataclass_fields__.keys())

    assert doc_fields == schema_fields
