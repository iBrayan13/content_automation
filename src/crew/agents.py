import inspect
import traceback
from typing import Any, List, Optional

from crewai import Agent
from langchain_core.language_models.chat_models import BaseChatModel

from src.core.dependencies import (
    get_prompt_manager,
    get_settings,
)
settings = get_settings()
prompt_manager = get_prompt_manager()


class ContentAgents:

    @staticmethod
    def _agent(
        llm: BaseChatModel, tools: List[Any] = []
    ) -> Optional[Agent]:
        """
        Creates an Agent instance with the specified LLM and tools.

        Args:
            llm (BaseChatModel): The language model to use for the agent.
            tools (List[Any], optional): A list of tools to be used by the agent. Defaults to an empty list.

        Returns:
            Optional[Agent]: The created Agent instance, or None if an error occurred.
        """
        agent_name = inspect.currentframe().f_code.co_name

        try:
            agent_prompt = prompt_manager.get_prompt(agent_name)
            if agent_prompt is None:
                raise NameError(f"Agent '{agent_name}' not found in prompt_manager.")
        except Exception as ex:
            exception_traceback = traceback.format_exc()
            print(
                f"StaticMethod: ContentAgents.analyzer_agent {type(ex)}:\n{exception_traceback}"
            )
            return None

        return Agent(**agent_prompt.get_agent_data(), tools=tools, llm=llm)