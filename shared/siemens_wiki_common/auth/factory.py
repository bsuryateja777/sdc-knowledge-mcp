from __future__ import annotations

from siemens_wiki_common.auth.base import ConfluenceAuthProvider
from siemens_wiki_common.auth.cookie_auth import CookieAuthProvider
from siemens_wiki_common.auth.pat_auth import PATAuthProvider
from siemens_wiki_common.config import ConfluenceInstance


def get_auth_provider(instance: ConfluenceInstance) -> ConfluenceAuthProvider:
    strategy = instance.auth_strategy.lower()
    if strategy == "cookie":
        return CookieAuthProvider(instance.jsessionid)
    if strategy == "pat":
        return PATAuthProvider(instance.pat)
    raise ValueError(
        f"Unknown auth strategy for instance {instance.name!r}: {instance.auth_strategy!r}"
    )
