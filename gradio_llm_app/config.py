"""Central configuration.

Every setting is read from the environment so that nothing sensitive is
hardcoded. Values fall back to the defaults used by the IBM Skills Network
lab environment, where credentials are injected automatically.

Copy `.env.example` to `.env` and fill it in to run outside that environment.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

try:  # python-dotenv is optional; the apps still run without it.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


def _env_str(name: str, default: str) -> str:
    return os.getenv(name, default)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    return int(raw) if raw else default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw else default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class WatsonxSettings:
    """Connection and generation settings for watsonx.ai."""

    url: str = field(
        default_factory=lambda: _env_str(
            "WATSONX_URL", "https://us-south.ml.cloud.ibm.com"
        )
    )
    project_id: str = field(
        default_factory=lambda: _env_str("WATSONX_PROJECT_ID", "skills-network")
    )
    # Only needed outside the hosted lab environment.
    api_key: str | None = field(default_factory=lambda: os.getenv("WATSONX_APIKEY"))

    chat_model_id: str = field(
        default_factory=lambda: _env_str(
            "CHAT_MODEL_ID", "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
        )
    )
    rag_model_id: str = field(
        default_factory=lambda: _env_str("RAG_MODEL_ID", "mistralai/mistral-medium-2505")
    )
    embedding_model_id: str = field(
        default_factory=lambda: _env_str(
            "EMBEDDING_MODEL_ID", "ibm/granite-embedding-278m-multilingual"
        )
    )

    max_new_tokens: int = field(default_factory=lambda: _env_int("MAX_NEW_TOKENS", 256))
    temperature: float = field(default_factory=lambda: _env_float("TEMPERATURE", 0.5))
    # Max tokens per chunk sent to the embedding model.
    embedding_truncate_input_tokens: int = field(
        default_factory=lambda: _env_int("EMBEDDING_TRUNCATE_INPUT_TOKENS", 512)
    )


@dataclass(frozen=True)
class RagSettings:
    """Chunking settings for the document pipeline."""

    chunk_size: int = field(default_factory=lambda: _env_int("CHUNK_SIZE", 1000))
    chunk_overlap: int = field(default_factory=lambda: _env_int("CHUNK_OVERLAP", 50))


@dataclass(frozen=True)
class ServerSettings:
    """Where the Gradio server binds."""

    host: str = field(default_factory=lambda: _env_str("GRADIO_SERVER_NAME", "127.0.0.1"))
    port: int = field(default_factory=lambda: _env_int("GRADIO_SERVER_PORT", 7860))
    share: bool = field(default_factory=lambda: _env_bool("GRADIO_SHARE", False))


watsonx = WatsonxSettings()
rag = RagSettings()
server = ServerSettings()
