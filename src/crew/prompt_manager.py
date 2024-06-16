from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, PrivateAttr


class TaskPrompt(BaseModel):
    task_name: str = Field(
        description="Name to identify the instance (same name that its method)"
    )
    description: str
    expected_output: str

    def get_task_data(self) -> dict:
        """
        Returns a dictionary containing the data of the task after excluding the "task_name" field.

        :return: A dictionary with the task data.
        :rtype: dict
        """
        return self.model_dump(exclude={"task_name"})


class AgentPrompt(BaseModel):
    agent_name: str = Field(
        description="Name to identify the instance (same name that its method)"
    )
    role: str
    goal: str
    backstory: str

    def get_agent_data(self) -> dict:
        """
        Returns a dictionary containing the data of the agent after excluding the "agent_name" field.

        :return: A dictionary with the agent data.
        :rtype: dict
        """
        return self.model_dump(exclude={"agent_name"})


class PromptManager(BaseModel):
    tasks: List[TaskPrompt]
    agents: List[AgentPrompt]

    _task_dict: dict = PrivateAttr()
    _agent_dict: dict = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        """
        Initializes the `_task_dict` and `_agent_dict` attributes of the `PromptManager` object.

        Args:
            __context (Any): The context object.

        Returns:
            None
        """
        self._task_dict = {task.task_name: task for task in self.tasks}
        self._agent_dict = {agent.agent_name: agent for agent in self.agents}

    def get_prompt(self, name: str) -> Optional[Union[AgentPrompt, TaskPrompt]]:
        """
        Retrieves a prompt by its name from either the task dictionary or the agent dictionary.

        Args:
            name (str): The name of the prompt to retrieve.

        Returns:
            Optional[Union[AgentPrompt, TaskPrompt]]: The prompt with the specified name, if found.
                Returns None if the prompt is not found in either dictionary.
        """
        if name in self._task_dict:
            return self._task_dict[name]

        elif name in self._agent_dict:
            return self._agent_dict[name]

        return None