from __future__ import annotations

import logging
import time
from typing import Callable, TypeVar

from azure.core.exceptions import HttpResponseError, ServiceRequestError, ServiceResponseError

logger = logging.getLogger(__name__)

T = TypeVar("T")

_TRANSIENT_STATUS_CODES = {408, 429, 500, 502, 503, 504}
# OpenAI SDK (used for Foundry embeddings) transient error class names --
# checked by name so this module doesn't need an `openai` import/dependency.
_TRANSIENT_OPENAI_ERRORS = {"APIConnectionError", "APITimeoutError", "RateLimitError", "InternalServerError"}


def _is_transient(exc: Exception) -> bool:
    if isinstance(exc, (ServiceRequestError, ServiceResponseError)):
        return True
    if isinstance(exc, HttpResponseError):
        return exc.status_code in _TRANSIENT_STATUS_CODES
    return type(exc).__name__ in _TRANSIENT_OPENAI_ERRORS


def retry_transient(fn: Callable[[], T], *, max_attempts: int = 3, base_delay: float = 0.5, label: str = "") -> T:
    """Retry fn() with exponential backoff on transient network/5xx/rate-limit
    errors. Re-raises immediately on non-transient errors (e.g. 4xx auth or
    validation failures) since retrying those can't help."""
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            if not _is_transient(exc) or attempt == max_attempts:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(
                "Transient error on attempt %d/%d for %s: %s -- retrying in %.1fs",
                attempt, max_attempts, label or getattr(fn, "__name__", "call"), exc, delay,
            )
            time.sleep(delay)
    raise last_exc  # pragma: no cover -- unreachable, loop always returns or raises
