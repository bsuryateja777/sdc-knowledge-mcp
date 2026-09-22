from __future__ import annotations

import html
import re

from bs4 import BeautifulSoup


def parse_confluence_storage(storage_html: str) -> str:
    """Convert Confluence storage format (XHTML-like XML) to clean plain text."""
    if not storage_html:
        return ""

    soup = BeautifulSoup(storage_html, "html.parser")

    for tag in soup.find_all(["ac:parameter", "ac:plain-text-body", "ac:image"]):
        tag.decompose()

    for macro in soup.find_all("ac:structured-macro"):
        macro.unwrap()

    text = soup.get_text(separator=" ", strip=True)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()
