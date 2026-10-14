"""Chainlit web interface for Career Agent."""

import os

if os.name == "nt":
    os.environ.pop("SSLKEYLOGFILE", None)
os.environ.pop("DATABASE_URL", None)

import chainlit as cl  # noqa: E402

from career_service import (  # noqa: E402
    ConfigurationError,
    build_career_guidance,
    format_guidance_markdown,
    safe_provider_error_message,
)


@cl.set_starters
async def set_starters() -> list[cl.Starter]:
    return [
        cl.Starter(
            label="I enjoy coding and math",
            message=(
                "I enjoy programming, mathematics, and finding patterns in data. "
                "What career path should I explore?"
            ),
        ),
        cl.Starter(
            label="I am creative and visual",
            message=(
                "I enjoy drawing, visual storytelling, and improving how apps look "
                "and feel. What career path fits me?"
            ),
        ),
        cl.Starter(
            label="I like security and puzzles",
            message=(
                "I enjoy networking, solving technical puzzles, and learning how to "
                "protect systems. Suggest a career path."
            ),
        ),
    ]


@cl.on_message
async def on_message(message: cl.Message) -> None:
    interests = message.content.strip()
    if len(interests) < 3:
        await cl.Message(
            content="Please tell me a little more—for example, a subject, hobby, or task you enjoy."
        ).send()
        return

    guidance = None
    error_message = None
    async with cl.Step(
        name="Creating your personalized career plan",
        type="tool",
        show_input=False,
    ) as step:
        try:
            guidance = await build_career_guidance(interests)
            step.output = f"Matched career: {guidance.career}"
        except ConfigurationError as error:
            step.is_error = True
            step.output = "The Career Agent setup is incomplete."
            error_message = f"**Setup needed:** {error}"
        except Exception as error:
            step.is_error = True
            step.output = "The AI service could not create the career plan."
            error_message = safe_provider_error_message(error)

    if error_message:
        await cl.Message(content=error_message).send()
        return

    if guidance is None:
        return

    await cl.Message(content=format_guidance_markdown(guidance)).send()
