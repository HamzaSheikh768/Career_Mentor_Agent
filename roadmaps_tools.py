"""Deterministic skill-roadmap tool used by the skill coaching agent."""

import re

from agents import function_tool


ROADMAPS = {
    "data scientist": (
        "Python fundamentals; NumPy and pandas; SQL; statistics and probability; "
        "machine learning; data visualization; portfolio projects and deployment"
    ),
    "web developer": (
        "HTML and CSS; JavaScript; a frontend framework; backend APIs; databases; "
        "testing, Git, accessibility, and deployment"
    ),
    "cybersecurity analyst": (
        "Networking fundamentals; Linux; Python or PowerShell; security concepts; "
        "threat analysis; SIEM practice; incident-response labs"
    ),
    "graphic designer": (
        "Design principles; typography and color; Figma; image editing; brand systems; "
        "UI/UX fundamentals; a focused portfolio"
    ),
    "software engineer": (
        "Programming fundamentals; data structures and algorithms; Git; databases; "
        "APIs; testing; system design basics; deployed portfolio projects"
    ),
    "ui ux designer": (
        "User research; information architecture; wireframing; Figma; prototyping; "
        "usability testing; accessibility; case-study portfolio"
    ),
    "digital marketer": (
        "Audience research; copywriting; content strategy; SEO; analytics; campaign "
        "experiments; a results-focused portfolio"
    ),
}


def normalize_career_key(career_field: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", career_field.casefold()).strip()


def lookup_career_roadmap(career_field: str) -> str:
    roadmap = ROADMAPS.get(normalize_career_key(career_field))
    if roadmap:
        return roadmap
    return (
        "No stored roadmap is available for this exact career. Create a sensible "
        "beginner-to-job-ready roadmap from your professional knowledge."
    )


@function_tool
def get_career_roadmap(career_field: str) -> str:
    """Return a reliable baseline skill roadmap for a career title."""
    return lookup_career_roadmap(career_field)
