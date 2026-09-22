from __future__ import annotations

import logging
from pathlib import Path

import azure.functions as func

from ingest_pipeline import run_ingestion
from siemens_wiki_common.config import get_settings, load_sources
from siemens_wiki_common.models import WikiSource

app = func.FunctionApp()

# Resolved relative to this file, not to shared/siemens_wiki_common's assumed
# repo depth -- keeps this Function App self-contained once repackaged for
# deployment (see scripts/build_function_zip.py), where shared/ and config/
# get copied to sit alongside this file instead of two levels up.
SOURCES_PATH = Path(__file__).parent / "config" / "sources.yaml"

# One codebase, deployed as two independent Function App resources -- each
# resource sets INGESTION_INSTANCE=wiki or INGESTION_INSTANCE=confluence as
# an app setting, so the same code only ever syncs its own instance. Local
# runs (INGESTION_INSTANCE unset) sync everything in config/sources.yaml.
#
# NOTE: unattended runs need a long-lived credential (PAT/service account)
# for whichever instance is deployed. A JSESSIONID cookie expires in 8-24h
# and requires manual refresh, so the timer trigger will start failing until
# PAT auth is granted for that instance. See CLAUDE.md/CLAUDE-1.md section 3
# and the plan's "Ingestion Trigger" note.


def _sources_for_this_deployment(settings) -> list[WikiSource]:
    sources = load_sources(path=SOURCES_PATH)
    if settings.ingestion_instance:
        sources = [s for s in sources if s.instance == settings.ingestion_instance]
    return sources


@app.timer_trigger(schedule="0 0 0 * * *", arg_name="timer", run_on_startup=False)
def sync_timer(timer: func.TimerRequest) -> None:
    """Nightly, incremental (see run_ingestion's docstring) -- only crawls
    pages modified since the last run. Cheap, but never sees deletions."""
    settings = get_settings()
    sources = _sources_for_this_deployment(settings)
    summary = run_ingestion(sources, settings)
    logging.info(
        "Scheduled incremental ingestion complete (instance=%s): %s",
        settings.ingestion_instance or "all", summary,
    )


@app.timer_trigger(schedule="0 0 2 * * 0", arg_name="timer", run_on_startup=False)
def sync_weekly_full(timer: func.TimerRequest) -> None:
    """Weekly (Sunday 02:00), full re-crawl -- incremental sync only ever adds
    or updates pages, it can't detect pages deleted from Confluence. This
    reconciles the index against reality on a schedule instead of relying on
    someone remembering to run --full/?full=true manually."""
    settings = get_settings()
    sources = _sources_for_this_deployment(settings)
    summary = run_ingestion(sources, settings, force_full=True)
    logging.info(
        "Scheduled full reconciliation complete (instance=%s): %s",
        settings.ingestion_instance or "all", summary,
    )


@app.route(route="sync", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def sync_http(req: func.HttpRequest) -> func.HttpResponse:
    """Manual re-run, protected by the function key. Useful while iterating on
    parsing/chunking without waiting for the nightly timer."""
    settings = get_settings()
    sources = _sources_for_this_deployment(settings)
    limit = req.params.get("limit")
    full = req.params.get("full", "").lower() in ("1", "true", "yes")
    summary = run_ingestion(
        sources, settings, limit=int(limit) if limit else None, force_full=full
    )
    return func.HttpResponse(
        f"instance={settings.ingestion_instance or 'all'} full={full} "
        f"pages_processed={summary.pages_processed} "
        f"pages_skipped_empty={summary.pages_skipped_empty} "
        f"chunks_indexed={summary.chunks_indexed}",
        status_code=200,
    )
