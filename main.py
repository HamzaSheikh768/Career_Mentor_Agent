import os

from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    AsyncOpenAI, 
    OpenAIChatCompletionsModel
)

from agents.run import RunConfig
from roadmaps_tools import get_career_roadmap

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client

)

config = RunConfig(
    model=model,
    tracing_disabled=True,
)

# Career Agent
career_agent = Agent(
    name="CareerAgent",
    instructions="Suggests career fields based on student interests.",
    model=model
)

#Skill Agent
skill_agent = Agent(
    name="SkillAgent",
    instructions="Provides skill-building plans based on the chosen career path.",
    model=model
)

#Job Agent
job_agent = Agent(
    name="JobAgent",
    instructions="You suggest real_world job roles and responsibilities.",
    model=model
)

def main():
    print("\U0001F393 Career Mentor Agent\n")
    interest = input("What are your Interests? -> ")

    result1 = Runner.run_sync(career_agent, interest, run_config=config)
    career_field = result1.final_output.strip()
    print("\n Suggested Career: ", career_field)

    result2 = Runner.run_sync(skill_agent, career_field, run_config=config)
    print("\n Required Skill:", result2.final_output)

    result3 = Runner.run_sync(job_agent, career_field, run_config=config)
    print("\n Possible Jobs:", result3.final_output)


if __name__ == "__main__":
    main()
