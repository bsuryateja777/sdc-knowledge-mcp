from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))

from siemens_wiki_common.config import get_instance, get_settings  # noqa: E402
from siemens_wiki_common.embeddings import FoundryEmbedder  # noqa: E402
from siemens_wiki_common.search_index import SearchIndexClient  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Sanity-check an Azure AI Search index")
    parser.add_argument("query", nargs="?", default="Siemens Data & AI Cloud", help="sample query to run")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--instance", default="wiki", help="which index to query (wiki | confluence)")
    args = parser.parse_args()

    settings = get_settings()
    index_name = get_instance(settings, args.instance).index_name
    index = SearchIndexClient(settings, index_name=index_name)
    embedder = FoundryEmbedder(settings)

    embedding = embedder.embed(args.query)
    results = index.hybrid_search(args.query, embedding, top_k=args.top_k)

    print(f"Query: {args.query!r} -> {len(results)} result(s)")
    for r in results:
        print(f"  - {r['title']!r} | {r['source_url']} | chunk preview: {r['content'][:80]!r}")


if __name__ == "__main__":
    main()
