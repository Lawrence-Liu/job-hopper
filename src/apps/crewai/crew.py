from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task


@CrewBase
class ResumeGenerator:
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
        )

    @agent
    def resume_enhancer(self) -> Agent:
        return Agent(
            config=self.agents_config["resume_enhancer"],
            verbose=True,
        )

    @agent
    def resume_stylist(self) -> Agent:
        return Agent(
            config=self.agents_config["resume_stylist"],
            verbose=True,
        )

    @task
    def extract_info_task(self) -> Task:
        return Task(
            config=self.tasks_config["extract_info_task"],
        )

    @task
    def enhance_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config["enhance_resume_task"],
        )

    @task
    def style_resume_task(self) -> Task:
        return Task(
            config=self.tasks_config["style_resume_task"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
