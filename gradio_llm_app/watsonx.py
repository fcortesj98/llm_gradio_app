"""Factories for the watsonx.ai LLM and embedding clients.

Both `apps/chatbot.py` and `apps/qabot.py` used to build these inline with
duplicated URLs, project IDs and parameter dicts. They live here instead.
"""

from __future__ import annotations

from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from langchain_ibm import WatsonxEmbeddings, WatsonxLLM

from .config import watsonx as settings


def _credentials() -> dict[str, str]:
    """Auth kwargs. The API key is omitted in the hosted lab environment."""
    creds = {"url": settings.url, "project_id": settings.project_id}
    if settings.api_key:
        creds["apikey"] = settings.api_key
    return creds


def build_llm(
    model_id: str | None = None,
    max_new_tokens: int | None = None,
    temperature: float | None = None,
) -> WatsonxLLM:
    """Return a LangChain-compatible watsonx.ai LLM."""
    params = {
        GenParams.MAX_NEW_TOKENS: max_new_tokens or settings.max_new_tokens,
        GenParams.TEMPERATURE: (
            settings.temperature if temperature is None else temperature
        ),
    }
    return WatsonxLLM(
        model_id=model_id or settings.chat_model_id,
        params=params,
        **_credentials(),
    )


def build_embeddings(model_id: str | None = None) -> WatsonxEmbeddings:
    """Return the embedding model used to index documents."""
    params = {
        EmbedParams.TRUNCATE_INPUT_TOKENS: settings.embedding_truncate_input_tokens,
        EmbedParams.RETURN_OPTIONS: {"input_text": True},
    }
    return WatsonxEmbeddings(
        model_id=model_id or settings.embedding_model_id,
        params=params,
        **_credentials(),
    )
