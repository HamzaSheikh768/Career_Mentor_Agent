"""Safe local launcher for the Chainlit interface on Windows."""

import os
import sys

if os.name == "nt":
    os.environ.pop("SSLKEYLOGFILE", None)
os.environ.pop("DATABASE_URL", None)

from chainlit.cli import cli


if __name__ == "__main__":
    sys.argv = ["chainlit", "run", "chainlit_app.py", *sys.argv[1:]]
    cli()
