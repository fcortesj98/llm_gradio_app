"""The retrieval-augmented generation pipeline behind the Q&A bot.

PDF -> pages -> chunks -> embeddings -> Chroma -> retriever -> answer.

Each step is its own function so it can be tested or swapped in isolation.
"""

from __future__ import annotations

from typing import Any

from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from .config import rag as settings
from .config import watsonx as watsonx_settings
from .watsonx import build_embeddings, build_llm


def resolve_path(file: Any) -> str:
    """Normalise whatever `gr.File` hands us into a filesystem path.

    Depending on the Gradio version and the component's `type`, this is either
    a plain `str`, a `NamedString`, or an object with a `.name` attribute.
    """
    if file is None:
        raise ValueError("No file was uploaded.")
    if isinstance(file, str):
        return file
    name = getattr(file, "name", None)
    if name:
        return name
    raise TypeError(f"Unsupported file input: {type(file)!r}")


def load_pdf(file: Any) -> list[Document]:
    """Read a PDF into one Document per page."""
    return PyPDFLoader(resolve_path(file)).load()


def split_documents(documents: list[Document]) -> list[Document]:
    """Break pages into overlapping chunks small enough to embed."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
    )
    return splitter.split_documents(documents)


def build_vector_store(chunks: list[Document]) -> Chroma:
    """Embed chunks into an in-memory Chroma collection."""
    return Chroma.from_documents(chunks, build_embeddings())


def build_retriever(file: Any) -> VectorStoreRetriever:
    """Run the full ingest pipeline and return a retriever over the result."""
    pages = load_pdf(file)
    chunks = split_documents(pages)
    return build_vector_store(chunks).as_retriever()


def answer_question(file: Any, query: str) -> str:
    """Answer `query` using only the contents of the uploaded PDF."""
    if not query or not query.strip():
        return "Please enter a question."

    chain = RetrievalQA.from_chain_type(
        llm=build_llm(model_id=watsonx_settings.rag_model_id),
        chain_type="stuff",
        retriever=build_retriever(file),
        return_source_documents=False,
    )
    return chain.invoke(query)["result"]
