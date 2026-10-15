"""Agent definitions and orchestration for personalized career guidance."""

from __future__ import annotations

import asyncio
import os
import re
from dataclasses import dataclass
from functools import lru_cache

# Apply this before importing the SDK, which initializes HTTPS clients.
if os.name == "nt":
    os.environ.pop("SSLKEYLOGFILE", None)

from agents import Agent, OpenAIChatCompletionsModel, Runner  # noqa: E402
from agents.run import RunConfig  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from openai import AsyncOpenAI  # noqa: E402

from roadmaps_tools import get_career_roadmap  # noqa: E402

load_dotenv()

DEFAULT_MODEL = "gemini-3.6-flash"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


class ConfigurationError(RuntimeError):
    """Raised when a required application setting is missing."""


def safe_provider_error_message(error: Exception) -> str:
    """Return a user-facing provider error without exposing response details."""
    status_code = getattr(error, "status_code", None)
    if status_code in {401, 403}:
        return (
            "The AI service rejected the configured credentials. Replace or reactivate "
            "the Gemini API key, restart the app, and try again."
        )
    if status_code == 429:
        return (
            "The AI service is temporarily rate-limited. Please wait a moment and "
            "try again."
        )
    return (
        "I couldn’t create your plan right now. Check the API key and model settings, "
        "then try again."
    )


@dataclass(frozen=True)
class CareerGuidance:
    career: str
    skills: str
    jobs: str


@dataclass(frozen=True)
class AgentRuntime:
    career_agent: Agent
    skill_agent: Agent
    job_agent: Agent
    run_config: RunConfig


@lru_cache(maxsize=1)
def get_runtime() -> AgentRuntime:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "GEMINI_API_KEY is missing. Add it to the environment variables and "
            "restart or redeploy the app."
        )

    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    client = AsyncOpenAI(api_key=api_key, base_url=GEMINI_BASE_URL)
    model = OpenAIChatCompletionsModel(model=model_name, openai_client=client)

    career_agent = Agent(
        name="Career Matcher",
        instructions=(
            "Match the student's interests to one realistic career. Return only the "
            "career title on one line, with no label, bullets, explanation, or markdown. "
            "Choose a specific, widely recognized role rather than a broad industry."
        ),
        model=model,
    )
    skill_agent = Agent(
        name="Skill Coach",
        instructions=(
            "Create a practical skill-building plan for the selected career. First call "
            "get_career_roadmap for a reliable baseline. Then provide 5 to 7 numbered "
            "steps ordered from beginner to job-ready. Each step must name the skill and "
            "one concrete practice activity. If the tool has no stored roadmap, use your "
            "own knowledge. Keep the plan concise and do not recommend paid products."
        ),
        tools=[get_career_roadmap],
        model=model,
    )
    job_agent = Agent(
        name="Job Explorer",
        instructions=(
            "Suggest 4 realistic entry-level or early-career job roles related to the "
            "selected career. For each role, give a one-sentence responsibility and one "
            "typical portfolio project. Do not invent live vacancies, employers, salaries, "
            "or guarantees. Use clear markdown bullets."
        ),
        model=model,
    )
    return AgentRuntime(
        career_agent=career_agent,
        skill_agent=skill_agent,
        job_agent=job_agent,
        run_config=RunConfig(model=model, tracing_disabled=True),
    )


def normalize_career_title(output: str) -> str:
    """Turn a narrowly prompted model response into a safe display title."""
    first_line = output.strip().splitlines()[0] if output.strip() else ""
    title = re.sub(r"^(career|suggested career)\s*:\s*", "", first_line, flags=re.I)
    title = title.strip(" -*_`\"'")
    if not title:
        raise ValueError("The career matcher returned an empty career title.")
    return title[:80]


async def build_career_guidance(interests: str) -> CareerGuidance:
    """Run the specialist agents and return one cohesive career plan."""
    cleaned_interests = " ".join(interests.split())
    if len(cleaned_interests) < 3:
        raise ValueError("Please describe at least one interest.")

    runtime = get_runtime()
    career_result = await Runner.run(
        runtime.career_agent,
        input=f"Student interests: {cleaned_interests}",
        run_config=runtime.run_config,
    )
    career = normalize_career_title(str(career_result.final_output))

    specialist_prompt = (
        f"Selected career: {career}\nStudent interests: {cleaned_interests}"
    )
    skill_result, job_result = await asyncio.gather(
        Runner.run(
            runtime.skill_agent,
            input=specialist_prompt,
            run_config=runtime.run_config,
        ),
        Runner.run(
            runtime.job_agent,
            input=specialist_prompt,
            run_config=runtime.run_config,
        ),
    )

    return CareerGuidance(
        career=career,
        skills=str(skill_result.final_output).strip(),
        jobs=str(job_result.final_output).strip(),
    )


def format_guidance_markdown(guidance: CareerGuidance) -> str:
    return (
        f"## Recommended career\n\n"
        f"### {guidance.career}\n\n"
        f"## Skill roadmap\n\n{guidance.skills}\n\n"
        f"## Roles to explore\n\n{guidance.jobs}"
    )
