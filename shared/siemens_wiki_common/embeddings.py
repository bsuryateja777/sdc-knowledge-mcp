from __future__ import annotations

from openai import AzureOpenAI

from siemens_wiki_common.config import Settings
from siemens_wiki_common.resilience import retry_transient


class FoundryEmbedder:
    """Embeds text via an OpenAI-family embedding model (e.g. text-embedding-3-small)
    deployed in an Azure AI Foundry project. Foundry exposes OpenAI-family models
    through the same endpoint shape as classic Azure OpenAI, so the `openai` SDK's
    AzureOpenAI client works unchanged -- this would NOT work for a non-OpenAI
    model (e.g. Claude) deployed in the same Foundry project; those need the
    azure-ai-inference SDK instead."""

    def __init__(self, settings: Settings):
        self._client = AzureOpenAI(
            azure_endpoint=settings.ai_foundry_endpoint,
            api_key=settings.ai_foundry_key,
            api_version=settings.ai_foundry_api_version,
        )
        self._deployment = settings.ai_foundry_embed_deployment

    def embed(self, text: str) -> list[float]:
        def _call():
            resp = self._client.embeddings.create(input=text, model=self._deployment)
            return resp.data[0].embedding

        return retry_transient(_call, label="embed")

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        def _call():
            resp = self._client.embeddings.create(input=texts, model=self._deployment)
            return [item.embedding for item in resp.data]

        return retry_transient(_call, label="embed_batch")
