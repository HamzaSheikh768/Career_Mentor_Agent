"""Vercel ASGI entrypoint for the Chainlit Career Agent."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import parse_qsl, urlencode


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = Path(tempfile.gettempdir()) / "career-agent-chainlit"

if os.name == "nt":
    os.environ.pop("SSLKEYLOGFILE", None)


def _prepare_writable_runtime() -> None:
    """Copy Chainlit's runtime assets to Vercel's writable temporary storage."""
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)

    for directory_name in (".chainlit", "public"):
        source = PROJECT_ROOT / directory_name
        if source.exists():
            shutil.copytree(
                source,
                RUNTIME_ROOT / directory_name,
                dirs_exist_ok=True,
            )

    markdown_source = PROJECT_ROOT / "chainlit.md"
    if markdown_source.exists():
        shutil.copy2(markdown_source, RUNTIME_ROOT / markdown_source.name)


_prepare_writable_runtime()
os.environ["CHAINLIT_APP_ROOT"] = str(RUNTIME_ROOT)

from chainlit.auth import ensure_jwt_secret  # noqa: E402
from chainlit.config import config, load_module  # noqa: E402
from chainlit.server import app as chainlit_app  # noqa: E402


CHAINLIT_APP = PROJECT_ROOT / "chainlit_app.py"
config.run.module_name = str(CHAINLIT_APP)
config.run.headless = True
config.run.watch = False

load_module(config.run.module_name)
ensure_jwt_secret()


class RestoreOriginalPath:
    """Restore the public URL path captured by Vercel's catch-all rewrite."""

    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] not in {"http", "websocket"}:
            await self.asgi_app(scope, receive, send)
            return

        query_items = parse_qsl(
            scope.get("query_string", b"").decode("utf-8"),
            keep_blank_values=True,
        )
        original_path = None
        forwarded_query = []

        for key, value in query_items:
            if key == "path" and original_path is None:
                original_path = value
            else:
                forwarded_query.append((key, value))

        if original_path is not None:
            public_path = f"/{original_path.lstrip('/')}"
            scope = dict(scope)
            scope["path"] = public_path
            scope["raw_path"] = public_path.encode("utf-8")
            scope["query_string"] = urlencode(forwarded_query, doseq=True).encode(
                "utf-8"
            )

        await self.asgi_app(scope, receive, send)


app = RestoreOriginalPath(chainlit_app)
