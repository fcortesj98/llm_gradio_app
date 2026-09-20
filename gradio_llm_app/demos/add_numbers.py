"""The smallest possible Gradio interface: two numbers in, their sum out."""

import gradio as gr


def add_numbers(first: float, second: float) -> float:
    return first + second


def build() -> gr.Interface:
    return gr.Interface(
        fn=add_numbers,
        inputs=[gr.Number(label="First number"), gr.Number(label="Second number")],
        outputs=gr.Number(label="Sum"),
        title="Add two numbers",
        allow_flagging="never",
    )
