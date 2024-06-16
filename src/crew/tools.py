from typing import Any
from textwrap import dedent

from crewai_tools import BaseTool
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain_openai import OpenAI as LangChainOpenAI
from openai import NotFoundError, OpenAI
from pydantic import Field, PrivateAttr

from src.core.dependencies import get_settings

settings = get_settings()


class SomeTool(BaseTool):
    name: str = "Some Tool"
    description: str = dedent("""
        Some description
    """)

    _property: str = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        """
        Initializes the `_property` attribute of the `SomeTool` object.

        Parameters:
            __context (Any): The context object.

        Returns:
            None
        """
        self._property = "Some property"

    def _run(self) -> str:
        """
        Runs the tool.

        Returns:
            str: Some string to return.
        """

        return "Some string to return"