# Gradio Demos + watsonx.ai Chat and RAG Apps

A small collection of [Gradio](https://www.gradio.app/) apps, going from a
two-field "add two numbers" demo up to a retrieval-augmented chatbot that
answers questions about a PDF you upload. The LLM-backed apps are served
through IBM watsonx.ai.

Every app is launched from a single entry point, so you no longer have to
edit a script to change the port or run a different demo.

## Project layout

```
.
├── run.py                     # launcher — python run.py <app>
├── pyproject.toml             # package metadata, optional editable install
├── requirements.txt           # direct dependencies
├── requirements-lock.txt      # exact pinned environment (full freeze)
├── .env.example               # copy to .env and fill in
├── data/                      # put local PDFs here (gitignored)
└── gradio_llm_app/
    ├── config.py              # all settings, read from the environment
    ├── watsonx.py             # LLM + embedding client factories
    ├── rag.py                 # PDF → chunks → Chroma → retriever → answer
    ├── cli.py                 # app registry and argument parsing
    ├── demos/
    │   ├── add_numbers.py
    │   ├── concat_sentences.py
    │   └── input_types.py
    └── apps/
        ├── chatbot.py         # plain watsonx.ai chatbot
        └── qabot.py           # RAG chatbot over an uploaded PDF
```

## The apps

| Name | Module | What it does | Needs watsonx.ai |
| --- | --- | --- | --- |
| `add-numbers` | `demos/add_numbers.py` | Two number inputs, returns their sum. | No |
| `concat-sentences` | `demos/concat_sentences.py` | Two text inputs joined into one sentence. | No |
| `input-types` | `demos/input_types.py` | Tour of Gradio's input components — slider, dropdown, checkbox group, radio, multiselect, checkbox — plus prefilled examples. | No |
| `chatbot` | `apps/chatbot.py` | Single-turn chatbot wired to a Llama model via `langchain-ibm`. | Yes |
| `qabot` | `apps/qabot.py` | RAG chatbot: upload a PDF, ask questions, get answers grounded in that document. | Yes |

## Setup

Python 3.10+ is required.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your credentials
```

To reproduce the exact environment this was developed against, use
`pip install -r requirements-lock.txt` instead.

## Running an app

```bash
python run.py --list            # show every available app
python run.py add-numbers       # run a demo
python run.py qabot             # run the RAG chatbot
```

Then open `http://127.0.0.1:7860`.

Useful flags:

```bash
python run.py chatbot --port 7861      # avoid a port clash
python run.py qabot --host 0.0.0.0     # expose on your network
python run.py qabot --share            # public Gradio share link
python run.py qabot --quiet            # silence dependency warnings
```

Defaults for host, port and share also come from `.env`
(`GRADIO_SERVER_NAME`, `GRADIO_SERVER_PORT`, `GRADIO_SHARE`), so you can set
them once instead of passing flags each time.

## The RAG chatbot (`qabot`)

`qabot` is the most involved app here. Upload a PDF, type a question, and the
answer is generated from the retrieved passages rather than from the model's
own memory.

The pipeline, one function per step in `gradio_llm_app/rag.py`:

1. **Load** — `PyPDFLoader` reads the uploaded file into one document per page.
2. **Split** — `RecursiveCharacterTextSplitter` breaks pages into overlapping
   chunks (`CHUNK_SIZE` 1000 characters, `CHUNK_OVERLAP` 50).
3. **Embed and index** — each chunk is embedded with
   `ibm/granite-embedding-278m-multilingual` and stored in an in-memory Chroma
   collection.
4. **Retrieve** — the vector store is exposed as a LangChain retriever.
5. **Answer** — a `RetrievalQA` chain (`chain_type="stuff"`) drops the
   retrieved chunks into the prompt and asks the LLM.

Notes and limits:

- The index is rebuilt on every question, so each query re-reads and re-embeds
  the whole PDF. Fine for a demo; cache the retriever per file if you want it
  to feel fast.
- The vector store is in memory only and disappears when the process exits.
- `return_source_documents=False`, so answers arrive without citations. Flip it
  in `rag.py` if you want to show which passages were used.
- Answers are capped by `MAX_NEW_TOKENS` (256), so long questions can get cut
  off mid-sentence.
- `EMBEDDING_TRUNCATE_INPUT_TOKENS` defaults to **512** here. The original lab
  script set it to `3`, which silently truncated every chunk to three tokens
  and made retrieval close to useless. Set it back via `.env` if you need the
  original behaviour for a graded exercise.

## Credentials

`apps/chatbot.py` and `apps/qabot.py` need access to IBM watsonx.ai. The
default `WATSONX_PROJECT_ID=skills-network` targets a hosted lab environment
where credentials are already provided — no API key needed there.

Anywhere else, set your own in `.env`:

```bash
WATSONX_APIKEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

`gradio_llm_app/config.py` reads these at import time and
`gradio_llm_app/watsonx.py` passes the API key through only when one is set.
Nothing is hardcoded, and `.env` is gitignored.

## Configuration reference

All settings live in `gradio_llm_app/config.py` and are overridable through
the environment. See `.env.example` for the full list with defaults.

| Variable | Default | Used by |
| --- | --- | --- |
| `WATSONX_URL` | `https://us-south.ml.cloud.ibm.com` | both LLM apps |
| `WATSONX_PROJECT_ID` | `skills-network` | both LLM apps |
| `WATSONX_APIKEY` | unset | both LLM apps, outside the lab |
| `CHAT_MODEL_ID` | `meta-llama/llama-4-maverick-17b-128e-instruct-fp8` | `chatbot` |
| `RAG_MODEL_ID` | `mistralai/mistral-medium-2505` | `qabot` |
| `EMBEDDING_MODEL_ID` | `ibm/granite-embedding-278m-multilingual` | `qabot` |
| `MAX_NEW_TOKENS` | `256` | both LLM apps |
| `TEMPERATURE` | `0.5` | both LLM apps |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `1000` / `50` | `qabot` |
| `GRADIO_SERVER_NAME` / `GRADIO_SERVER_PORT` / `GRADIO_SHARE` | `127.0.0.1` / `7860` / `false` | all apps |

## Gradio basics used here

- **`gr.Interface(fn=..., inputs=..., outputs=...)`** — wraps a Python
  function in a UI. Inputs are passed as positional arguments to `fn`; the
  return value populates the outputs.
- **`label=`** — the field name shown above a component.
- **`info=`** — smaller helper text under the label.
- **`title=` / `description=`** — set at the `Interface` level, not on
  individual components.
- **`examples=`** — clickable rows that prefill every input at once.
- **`allow_flagging="never"`** — hides the flag button.
- **`gr.File(type="filepath")`** — hands your function a path to the uploaded
  file rather than its bytes.

## What changed from the original layout

If you are coming from the flat version of this project:

| Before | Now |
| --- | --- |
| `gradio_demo.py` | `gradio_llm_app/demos/add_numbers.py` |
| `gradio_demo_sentences.py` | `gradio_llm_app/demos/concat_sentences.py` |
| `common_input_types.py` | `gradio_llm_app/demos/input_types.py` |
| `simple_llm.py` | `gradio_llm_app/apps/chatbot.py` |
| `qabot.py` | `gradio_llm_app/apps/qabot.py` + `gradio_llm_app/rag.py` |

Behavioural changes worth knowing about:

- Each module now exposes `build()` and returns its `Interface` instead of
  launching on import, so importing one no longer starts a server.
- Model IDs, URLs and generation parameters were duplicated across
  `simple_llm.py` and `qabot.py`; they are now in `config.py` once.
- `qabot.py` used to launch on `0.0.0.0` with `share=True` while every other
  script used `127.0.0.1`. All apps now default to localhost, with sharing
  opt-in via `--share`.
- The blanket `warnings.filterwarnings('ignore')` at the top of `qabot.py` is
  now opt-in behind `--quiet`.
- Unused `huggingface_hub` and `ModelInference` imports were dropped.
- `requirements.txt` lists direct dependencies; the original 130-line freeze
  is preserved as `requirements-lock.txt`.
