# Career Agent

A multi-agent career mentor powered by the OpenAI Agents SDK, Gemini's OpenAI-compatible API, and a Chainlit web interface.

## What it does

1. Matches a student's interests to one realistic career.
2. Builds a beginner-to-job-ready skill roadmap.
3. Suggests related entry-level roles, responsibilities, and portfolio projects.

## Setup

This project uses Python 3.12 and `uv`.

```powershell
uv sync
```

Create a `.env` file:

```dotenv
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.6-flash
```

`GEMINI_MODEL` is optional. The default is `gemini-3.6-flash`.

## Run the Chainlit UI

```powershell
uv run python run_ui.py
```

Then open `http://localhost:8000` if the browser does not open automatically.

## Run in the terminal

```powershell
uv run python main.py
```

## Run tests

```powershell
uv run python -m unittest discover -s tests -v
```

The application removes `SSLKEYLOGFILE` from its own Windows process before creating HTTPS clients. This avoids a native OpenSSL crash in some uv-managed Python environments without changing system settings.
