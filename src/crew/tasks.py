import inspect
import traceback
from typing import Any, List, Optional

from crewai import Agent, Task

from src.core.dependencies import get_prompt_manager

prompt_manager = get_prompt_manager()

class ContentTasks:

    @staticmethod
    def choose_story_task(agent: Agent, tools: List[Any] = []) -> Optional[Task]:
        """
        Creates a Task object.

        Args:
            agent (Agent): The Agent object that will perform the task.
            tools (List[Any], optional): A list of tools for the Agent. Defaults to an empty list.

        Returns:
            Task: A Task object with the specified description, agent, expected output, and tools.
        """
        task_name = inspect.currentframe().f_code.co_name

        try:
            task_prompt = prompt_manager.get_prompt(task_name)
            if task_prompt is None:
                raise NameError(f"Task '{task_name}' not found in prompt_manager.")
        except Exception as ex:
            exception_traceback = traceback.format_exc()
            print(
                f"StaticMethod: ContentTasks.choose_story_task {type(ex)}:\n{exception_traceback}"
            )
            return None

        return Task(
            **task_prompt.get_task_data(),
            agent=agent,
            tools=tools,
        )
    

    @staticmethod
    def script_task(agent: Agent, tools: List[Any] = []) -> Optional[Task]:
        """
        Creates a Task object.

        Args:
            agent (Agent): The Agent object that will perform the task.
            tools (List[Any], optional): A list of tools for the Agent. Defaults to an empty list.

        Returns:
            Task: A Task object with the specified description, agent, expected output, and tools.
        """
        task_name = inspect.currentframe().f_code.co_name

        try:
            task_prompt = prompt_manager.get_prompt(task_name)
            if task_prompt is None:
                raise NameError(f"Task '{task_name}' not found in prompt_manager.")
        except Exception as ex:
            exception_traceback = traceback.format_exc()
            print(
                f"StaticMethod: ContentTasks.script_task {type(ex)}:\n{exception_traceback}"
            )
            return None

        return Task(
            **task_prompt.get_task_data(),
            agent=agent,
            tools=tools,
        )
    
    @staticmethod
    def speech_task(agent: Agent, tools: List[Any] = []) -> Optional[Task]:
        """
        Creates a Task object.

        Args:
            agent (Agent): The Agent object that will perform the task.
            tools (List[Any], optional): A list of tools for the Agent. Defaults to an empty list.

        Returns:
            Task: A Task object with the specified description, agent, expected output, and tools.
        """
        task_name = inspect.currentframe().f_code.co_name

        try:
            task_prompt = prompt_manager.get_prompt(task_name)
            if task_prompt is None:
                raise NameError(f"Task '{task_name}' not found in prompt_manager.")
        except Exception as ex:
            exception_traceback = traceback.format_exc()
            print(
                f"StaticMethod: ContentTasks.speech_task {type(ex)}:\n{exception_traceback}"
            )
            return None

        return Task(
            **task_prompt.get_task_data(),
            agent=agent,
            tools=tools,
        )
    
    @staticmethod
    def img_prompts_task(agent: Agent, tools: List[Any] = []) -> Optional[Task]:
        """
        Creates a Task object.

        Args:
            agent (Agent): The Agent object that will perform the task.
            tools (List[Any], optional): A list of tools for the Agent. Defaults to an empty list.

        Returns:
            Task: A Task object with the specified description, agent, expected output, and tools.
        """
        task_name = inspect.currentframe().f_code.co_name

        try:
            task_prompt = prompt_manager.get_prompt(task_name)
            if task_prompt is None:
                raise NameError(f"Task '{task_name}' not found in prompt_manager.")
        except Exception as ex:
            exception_traceback = traceback.format_exc()
            print(
                f"StaticMethod: ContentTasks.img_prompts_task {type(ex)}:\n{exception_traceback}"
            )
            return None

        return Task(
            **task_prompt.get_task_data(),
            agent=agent,
            tools=tools,
        )