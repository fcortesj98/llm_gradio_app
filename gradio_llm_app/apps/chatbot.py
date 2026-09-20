"""A single-turn chatbot backed by a watsonx.ai model.

Previously `simple_llm.py`. The model is created lazily so that importing this
module (for example, from the launcher's registry) does not require
credentials.
"""

from __future__ import annotations

import gradio as gr
from langchain_ibm import WatsonxLLM

from ..watsonx import build_llm

_llm: WatsonxLLM | None = None


def _get_llm() -> WatsonxLLM:
    global _llm
    if _llm is None:
        _llm = build_llm()
    return _llm


def generate_response(prompt: str) -> str:
    if not prompt or not prompt.strip():
        return "Please enter a question."
    return _get_llm().invoke(prompt)


def build() -> gr.Interface:
    return gr.Interface(
        fn=generate_response,
        inputs=gr.Textbox(
            label="Input", lines=2, placeholder="Type your question here..."
        ),
        outputs=gr.Textbox(label="Output"),
        title="Watsonx.ai Chatbot",
        description="Ask any question and the chatbot will try to answer.",
        allow_flagging="never",
    )
