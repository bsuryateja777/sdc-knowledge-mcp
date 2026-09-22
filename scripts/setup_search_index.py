from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))

from siemens_wiki_common.config import get_instance, get_settings  # noqa: E402
from siemens_wiki_common.search_index import ensure_index  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/update an Azure AI Search index from schema.json")
    parser.add_argument(
        "--instance",
        default="wiki",
        help="which Confluence instance's index to create (wiki | confluence), default: wiki",
    )
    args = parser.parse_args()

    settings = get_settings()
    index_name = get_instance(settings, args.instance).index_name
    ensure_index(settings, index_name=index_name)
    print(f"Index '{index_name}' created/updated at {settings.azure_search_endpoint}")


if __name__ == "__main__":
    main()
