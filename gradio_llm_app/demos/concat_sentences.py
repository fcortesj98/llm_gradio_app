"""Two text inputs joined into one sentence — adds labels and a title."""

import gradio as gr


def concatenate_sentences(first: str, second: str) -> str:
    return f"{first} {second}"


def build() -> gr.Interface:
    return gr.Interface(
        fn=concatenate_sentences,
        inputs=[
            gr.Text(label="First sentence"),
            gr.Text(label="Second sentence"),
        ],
        outputs=gr.Text(label="Concatenated result"),
        title="Sentences to concatenate",
        allow_flagging="never",
    )
