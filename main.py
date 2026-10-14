"""Command-line entry point for Career Agent."""

import asyncio
import os

# Some Windows environments inject SSL key logging. The uv-managed Python
# build can crash while creating an HTTPS context when this variable is set.
if os.name == "nt":
    os.environ.pop("SSLKEYLOGFILE", None)

from career_service import (  # noqa: E402
    ConfigurationError,
    build_career_guidance,
    format_guidance_markdown,
    safe_provider_error_message,
)


async def run_cli() -> None:
    print("Career Agent\n")
    interest = input("What are your interests? -> ").strip()

    if len(interest) < 3:
        print("\nPlease describe at least one interest so I can guide you.")
        return

    try:
        guidance = await build_career_guidance(interest)
    except ConfigurationError as error:
        print(f"\nConfiguration error: {error}")
        return
    except Exception as error:
        print("\n" + safe_provider_error_message(error))
        return

    print("\n" + format_guidance_markdown(guidance))


def main() -> None:
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
