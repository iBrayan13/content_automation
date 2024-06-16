import json
from typing import Any, Dict, Optional

from crewai import Crew


class AgentService:
    def __init__(self, crew: Crew) -> None:
        """
        Initializes the AgentService object with the given crew.

        Args:
            crew (Crew): An instance of the Crew class representing the crew.

        Returns:
            None
        """
        self.crew = crew

    def run(self, inputs: Optional[Dict[str, Any]] = None):
        """
        Runs the agent service with the given inputs.

        Args:
            inputs (Optional[Dict[str, Any]]): Optional dictionary of inputs for the agent service.
        """
        data = self.crew.kickoff(inputs)

        if isinstance(data, str):
            data = json.loads(data)

        return data