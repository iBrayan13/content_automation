from crewai import Crew

from src.core.settings import GlobalSettings
from src.crew.prompt_manager import PromptManager
from src.crew.prompts import prompt
from src.services.agent_service import AgentService


def get_settings() -> GlobalSettings:
    """
    Returns an instance of the GlobalSettings class.

    :return: An instance of the GlobalSettings class.
    :rtype: GlobalSettings
    """
    return GlobalSettings()


def get_agent_service(crew: Crew) -> AgentService:
    """
    Creates an instance of the AgentService class with the given crew and returns it.

    :param crew: An instance of the Crew class representing the crew.
    :type crew: Crew
    :return: An instance of the AgentService class.
    :rtype: AgentService
    """
    return AgentService(crew)


def get_prompt_manager() -> PromptManager:
    """
    Returns an instance of the PromptManager class initialized with the provided prompt.

    :return: An instance of the PromptManager class.
    :rtype: PromptManager
    """
    return PromptManager(**prompt)