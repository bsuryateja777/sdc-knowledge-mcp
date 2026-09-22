from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ingestion"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))

from ingest_pipeline import run_ingestion  # noqa: E402
from siemens_wiki_common.config import get_settings, load_sources  # noqa: E402
from siemens_wiki_common.models import WikiSource  # noqa: E402


def parse_source(value: str) -> WikiSource:
    parts = value.split(":")
    if len(parts) == 2:
        instance, space_key, root_page_id = "wiki", parts[0], parts[1]
    elif len(parts) == 3:
        instance, space_key, root_page_id = parts
    else:
        raise argparse.ArgumentTypeError(
            "expected format space_key:root_page_id or instance:space_key:root_page_id, "
            "e.g. en:295931756 or confluence:SDCOPSL1:501414852"
        )
    return WikiSource(space_key=space_key, root_page_id=root_page_id, label="cli-override", instance=instance)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Confluence -> Azure AI Search ingestion locally")
    parser.add_argument("--source", type=parse_source, help="space_key:root_page_id override (default: config/sources.yaml)")
    parser.add_argument("--limit", type=int, default=None, help="only process the first N pages per source")
    parser.add_argument("--dry-run", action="store_true", help="parse+chunk but skip embedding/upload")
    parser.add_argument(
        "--full", action="store_true",
        help="force a full crawl, bypassing incremental lastModified filtering "
        "(also catches deletions/drift that incremental sync can't)",
    )
    args = parser.parse_args()

    settings = get_settings()
    sources = [args.source] if args.source else load_sources()

    print(f"Ingesting {len(sources)} source(s), limit={args.limit}, dry_run={args.dry_run}, full={args.full}")
    summary = run_ingestion(sources, settings, limit=args.limit, dry_run=args.dry_run, force_full=args.full)
    print(
        f"pages_processed={summary.pages_processed} "
        f"pages_skipped_empty={summary.pages_skipped_empty} "
        f"chunks_indexed={summary.chunks_indexed}"
    )


if __name__ == "__main__":
    main()
