"""Single entry point for every app in this project.

    python run.py --list
    python run.py qabot
    python run.py add-numbers --port 7861

Each target is imported lazily, so the lightweight demos run without the
watsonx.ai dependencies being importable.
"""

from __future__ import annotations

import argparse
import importlib
import warnings

from .config import server as server_settings

# name -> (module path, one-line description)
REGISTRY: dict[str, tuple[str, str]] = {
    "add-numbers": (
        "gradio_llm_app.demos.add_numbers",
        "Two number inputs, returns their sum.",
    ),
    "concat-sentences": (
        "gradio_llm_app.demos.concat_sentences",
        "Two text inputs joined into one sentence.",
    ),
    "input-types": (
        "gradio_llm_app.demos.input_types",
        "Tour of Gradio's input components, with examples.",
    ),
    "chatbot": (
        "gradio_llm_app.apps.chatbot",
        "Single-turn chatbot backed by a watsonx.ai model.",
    ),
    "qabot": (
        "gradio_llm_app.apps.qabot",
        "RAG chatbot: upload a PDF and ask questions about it.",
    ),
}


def _print_registry() -> None:
    width = max(len(name) for name in REGISTRY)
    print("Available apps:\n")
    for name, (_, description) in REGISTRY.items():
        print(f"  {name:<{width}}  {description}")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="run.py", description="Launch one of the Gradio apps in this project."
    )
    parser.add_argument(
        "app", nargs="?", choices=sorted(REGISTRY), help="Which app to launch."
    )
    parser.add_argument(
        "--list", action="store_true", help="List the available apps and exit."
    )
    parser.add_argument("--host", default=server_settings.host, help="Bind address.")
    parser.add_argument("--port", type=int, default=server_settings.port, help="Port.")
    parser.add_argument(
        "--share",
        action="store_true",
        default=server_settings.share,
        help="Create a public Gradio share link.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress Python warnings from the dependency stack.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.list or not args.app:
        _print_registry()
        return 0 if args.list else 1

    if args.quiet:
        warnings.filterwarnings("ignore")

    module_path, _ = REGISTRY[args.app]
    interface = importlib.import_module(module_path).build()
    interface.launch(
        server_name=args.host, server_port=args.port, share=args.share
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
