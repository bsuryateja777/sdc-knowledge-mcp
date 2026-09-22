import pytest

from siemens_wiki_common.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []


def test_text_shorter_than_chunk_size_returns_single_chunk():
    text = "one two three"
    assert chunk_text(text, chunk_size=10, overlap=2) == [text]


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("a b c", chunk_size=5, overlap=5)


def test_chunks_overlap_and_cover_all_words():
    words = [f"w{i}" for i in range(12)]
    text = " ".join(words)
    chunks = chunk_text(text, chunk_size=5, overlap=2)

    assert chunks[0] == "w0 w1 w2 w3 w4"
    # step = chunk_size - overlap = 3
    assert chunks[1] == "w3 w4 w5 w6 w7"
    # last chunk always reaches the final word
    assert chunks[-1].split()[-1] == "w11"


def test_last_chunk_does_not_duplicate_full_previous_chunk():
    text = " ".join(f"w{i}" for i in range(6))
    chunks = chunk_text(text, chunk_size=5, overlap=2)
    assert len(chunks) == 2
