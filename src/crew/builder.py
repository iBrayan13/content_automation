from crewai import Crew, Process
from langchain_openai import ChatOpenAI

from src.crew.tasks import ContentTasks
from src.crew.agents import ContentAgents
from src.crew.tools import SomeTool

class ContentCrewBuilder:

    @staticmethod
    def build(model_name: str, max_rpm: int) -> Crew:
        """
        Builds and returns a Crew object based on the provided  model name.

        :param model_name: The name of the model.
        :type model_name: str
        :param max_rpm: The maximum number of requests per minute.
        :type max_rpm: int
        :return: A Crew object with the specified agents, tasks, process, memory, cache, and manager_llm.
        :rtype: Crew
        """

        # setup llms
        llm = ChatOpenAI(model=model_name, temperature=0.65)

        # setup tools
        some_tool = SomeTool()

        # setup agents
        _agent = ContentAgents._agent(
            tools=[some_tool], llm=llm
        )

        _task = ContentTasks._task(
            _agent, tools=[some_tool]
        )

        return Crew(
            agents=[
                _agent
            ],
            tasks=[
                _task
            ],
            process=Process.hierarchical,
            memory=True,
            cache=True,
            manager_llm=llm,
            max_rpm=max_rpm,
        )