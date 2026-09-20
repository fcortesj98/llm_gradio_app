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

  opt-in via `--share`.
- The blanket `warnings.filterwarnings('ignore')` at the top of `qabot.py` is
  now opt-in behind `--quiet`.
- Unused `huggingface_hub` and `ModelInference` imports were dropped.
- `requirements.txt` lists direct dependencies; the original 130-line freeze
  is preserved as `requirements-lock.txt`.
