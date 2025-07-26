from agents import function_tool

@function_tool
def get_career_roadmap(career_field: str) -> str:
    """Return a skill roadmaps for the given career."""
    raodmaps = {
               "Data Scientist": "1. Python, 2. Pandas/Numpy, 3. Machine Learning, 4. SQL, 5. Visualization",
               "Web Developer": "1. HTML/CSS, 2. JavaScript, 3. React/Angular, 4. Backend (Node/Python), 5. Deployment",
               "Cybersecurity Analyst": "1. Networking Basics, 2. Linux, 3. Security+, 4. Threat Analysis, 5. SIEM tools",
               "Graphic Designer": "1. Figma 2. Photoshop 3. UI/UX Designer 4. Canva 5. Portfolio Designer"
    }
    return  raodmaps.get(career_field.lower(), "Roadmap not found. Please try another career.")