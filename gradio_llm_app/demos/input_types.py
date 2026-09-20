"""A tour of Gradio's input components, all feeding one function.

Slider, dropdown, checkbox group, radio, multiselect dropdown and checkbox,
plus `examples=` rows that prefill every field at once.
"""

import gradio as gr


def sentence_builder(
    quantity: int,
    tech_worker_type: str,
    countries: list[str],
    place: str,
    activity_list: list[str],
    morning: bool,
) -> str:
    origins = " and ".join(countries) if countries else "somewhere"
    activities = " and ".join(activity_list) if activity_list else "did nothing"
    time_of_day = "morning" if morning else "night"
    return (
        f"The {quantity} {tech_worker_type}s from {origins} went to the {place} "
        f"where they {activities} until the {time_of_day}"
    )


def build() -> gr.Interface:
    return gr.Interface(
        fn=sentence_builder,
        inputs=[
            gr.Slider(3, 20, value=4, step=1, label="Count", info="Choose between 3 and 20"),
            gr.Dropdown(
                ["Data Scientist", "Software Developer", "Software Engineer"],
                value="Data Scientist",
                label="Tech worker type",
                info="Will add more tech worker types later!",
            ),
            gr.CheckboxGroup(
                ["Canada", "Japan", "France"],
                label="Countries",
                info="Where are they from?",
            ),
            gr.Radio(
                ["office", "restaurant", "meeting room"],
                value="office",
                label="Location",
                info="Where did they go?",
            ),
            gr.Dropdown(
                ["partied", "brainstormed", "coded", "fixed bugs"],
                value=["brainstormed", "fixed bugs"],
                multiselect=True,
                label="Activities",
                info="Which activities did they perform?",
            ),
            gr.Checkbox(label="Morning", info="Did they do it in the morning?"),
        ],
        outputs=gr.Text(label="Sentence"),
        title="Common input types",
        examples=[
            [3, "Software Developer", ["Canada", "Japan"], "restaurant", ["coded", "fixed bugs"], True],
            [4, "Data Scientist", ["Japan"], "office", ["brainstormed", "partied"], False],
            [10, "Software Engineer", ["Canada", "France"], "meeting room", ["brainstormed"], False],
            [8, "Data Scientist", ["France"], "restaurant", ["coded"], True],
        ],
        allow_flagging="never",
    )
