from __future__ import annotations

from abc import ABC, abstractmethod


class ConfluenceAuthProvider(ABC):
    """Strategy interface so ConfluenceClient never knows whether it's using a
    cookie or a PAT. Swapping strategies is a config change (WIKI_AUTH_STRATEGY),
    not a code change."""

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        """Headers to merge into every Confluence REST request."""

    def refresh(self) -> None:
        """Called by ConfluenceClient on a 401/403. Default: nothing to do."""
        return None
