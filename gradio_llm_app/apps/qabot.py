"""RAG chatbot: upload a PDF, ask questions about it.

This module is only the UI layer. The retrieval pipeline lives in
`gradio_llm_app.rag`.
"""

from __future__ import annotations

import gradio as gr

from ..rag import answer_question


def build() -> gr.Interface:
    return gr.Interface(
        fn=answer_question,
        inputs=[
            gr.File(
                label="Upload PDF File",
                file_count="single",
                file_types=[".pdf"],
                type="filepath",
            ),
            gr.Textbox(
                label="Input Query", lines=2, placeholder="Type your question here..."
            ),
        ],
        outputs=gr.Textbox(label="Output"),
        title="RAG Chatbot",
        description=(
            "Upload a PDF document and ask any question. The chatbot will try "
            "to answer using the provided document."
        ),
        allow_flagging="never",
    )
