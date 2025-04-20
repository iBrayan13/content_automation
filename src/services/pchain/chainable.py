import json
from typing import Any, Literal

import instructor
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel
from anthropic import AsyncAnthropic
from anthropic.types.text_block import TextBlock
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.settings import Settings
from src.services.pchain.responses import Response
from src.services.pchain.chain_prompt_manager import ClientPrompt


class UnsupportedContentTypeError(Exception):
    pass


class APICallError(Exception):
    pass


class MinimalChainable:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model_supported_types = {
            "openai": {"text", "image"},
            "anthropic": {"text", "image"},
            "deepseek": {"text"},
        }

        self.openai_client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.anthropic_client = AsyncAnthropic(api_key=self.settings.ANTHROPIC_API_KEY)
        self.deepseek_client = AsyncOpenAI(api_key=self.settings.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

    def _get_instructor(
        self, client: AsyncOpenAI | AsyncAnthropic
    ) -> instructor.AsyncInstructor:
        if isinstance(client, AsyncOpenAI):
            return instructor.from_openai(client)
        elif isinstance(client, AsyncAnthropic):
            return instructor.from_anthropic(client)

    def _convert_value_to_string(self, value: Any) -> str:
        """Convert any value to a string representation"""
        if isinstance(value, dict | BaseModel):
            return json.dumps(value if isinstance(value, dict) else value.model_dump())
        elif isinstance(value, list):
            if not value:  # Empty list
                return "[]"
            return json.dumps(value)
        else:
            return str(value)

    def _prepare_content_for_anthropic(
        self, prompt: ClientPrompt, context: dict[str, Any]
    ) -> str:
        """Prepare content for Anthropic's newer API format"""
        # Start with the prompt
        content = prompt.prompt

        # For each content key, append the content with clear separation
        for key in prompt.content_keys:
            if key in context:
                try:
                    value = context[key]
                    value_str = self._convert_value_to_string(value)
                    content += f"\n\n{key}:\n{value_str}"
                except Exception as e:
                    logger.error(f"Error preparing content for key {key}: {str(e)}")
                    content += f"\n\n{key}:\n{str(context[key])}"

        return content

    def _prepare_content_for_openai(
        self, prompt: ClientPrompt, context: dict[str, Any]
    ) -> str:
        """Prepare content for OpenAI's API format"""
        # Start with the base prompt
        content = prompt.prompt

        # For each content key, append the content with clear separation
        for key in prompt.content_keys:
            if key in context:
                try:
                    value = context[key]
                    value_str = self._convert_value_to_string(value)
                    content += f"\n\n{key}:\n{value_str}"
                except Exception as e:
                    logger.error(f"Error preparing content for key {key}: {str(e)}")
                    content += f"\n\n{key}:\n{str(context[key])}"

        # Return the message in OpenAI's expected format
        return content
    
    def _prepare_content_for_deepseek(
        self, prompt: ClientPrompt, context: dict[str, Any]
    ) -> str:
        """Prepare content for DeepSeek's API format"""
        # Start with the base prompt
        content = prompt.prompt

        # For each content key, append the content with clear separation
        for key in prompt.content_keys:
            if key in context:
                try:
                    value = context[key]
                    value_str = self._convert_value_to_string(value)
                    content += f"\n\n{key}:\n{value_str}"
                except Exception as e:
                    logger.error(f"Error preparing content for key {key}: {str(e)}")
                    content += f"\n\n{key}:\n{str(context[key])}"

        # Return the message in DeepSeek's expected format
        return content

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _handle_anthropic_call(
        self, prompt: ClientPrompt, context: dict[str, Any]
    ) -> Response:
        try:
            content = self._prepare_content_for_anthropic(prompt, context)

            if prompt.return_model is not None:
                llm = self._get_instructor(self.anthropic_client)
                response = await llm.chat.completions.create(
                    model=self.settings.ANTHROPIC_MODEL_NAME,
                    messages=[{"role": "user", "content": content}],
                    response_model=prompt.return_model,
                    max_tokens=4096,
                    temperature=0,
                )

            else:
                message = await self.anthropic_client.messages.create(
                    model=self.settings.ANTHROPIC_MODEL_NAME,
                    max_tokens=4096,
                    temperature=0,
                    messages=[{"role": "user", "content": content}],
                )

                if isinstance(message.content[0], TextBlock):
                    response = message.content[0].text
                else:
                    response = ""

            return Response(response=response)
        except Exception as e:
            logger.error(f"Error in Anthropic API call: {str(e)}")
            raise APICallError(f"Error in Anthropic API call: {str(e)}") from e

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _handle_openai_call(
        self, prompt: ClientPrompt, context: dict[str, Any]
    ) -> Response:
        try:
            message = self._prepare_content_for_openai(prompt, context)

            if prompt.return_model is not None:
                llm = self._get_instructor(self.openai_client)
                response_obj = await llm.chat.completions.create(
                    model=self.settings.OPENAI_MODEL_NAME,
                    messages=[{"role": "user", "content": message}],
                    response_model=prompt.return_model,
                    temperature=0,
                )

                return Response(response=response_obj)
            else:
                raw_response = await self.openai_client.chat.completions.create(
                    model=self.settings.OPENAI_MODEL_NAME,
                    messages=[{"role": "user", "content": message}],
                    temperature=0,
                )

                response = raw_response.choices[0].message.content

                return Response(response=response)

        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise APICallError(f"Error in OpenAI API call: {str(e)}") from e
    
    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _handle_deepseek_call(
        self, prompt: ClientPrompt, context: dict[str, Any]
    ) -> Response:
        try:
            message = self._prepare_content_for_deepseek(prompt, context)

            if prompt.return_model is not None:
                llm = self._get_instructor(self.deepseek_client)
                response_obj = await llm.chat.completions.create(
                    model=self.settings.DEEPSEEK_MODEL_NAME,
                    messages=[{"role": "user", "content": message}],
                    response_model=prompt.return_model,
                    temperature=0,
                )

                return Response(response=response_obj)
            else:
                raw_response = await self.deepseek_client.chat.completions.create(
                    model=self.settings.DEEPSEEK_MODEL_NAME,
                    messages=[{"role": "user", "content": message}],
                    temperature=0,
                )

                response = raw_response.choices[0].message.content

                return Response(response=response)

        except Exception as e:
            logger.error(f"Error in DeepSeek API call: {str(e)}")
            raise APICallError(f"Error in DeepSeek API call: {str(e)}") from e

    async def _handle_prompt(
        self,
        client: Literal['openai', 'anthropic', 'deepseek'],
        prompt: ClientPrompt,
        context: dict[str, Any],
    ) -> Response:
        if client == 'openai':
            return await self._handle_openai_call(prompt, context)
        elif client == 'deepseek':
            return await self._handle_deepseek_call(prompt, context)
        elif client == 'anthropic':
            return await self._handle_anthropic_call(prompt, context)
        else:
            raise ValueError(f"Unsupported client type: {client}")

    async def run(
        self,
        client: Literal['openai', 'anthropic', 'deepseek'],
        prompts: list[ClientPrompt],
        context: dict[str, Any] | None = None,
        returns_model: dict[int, type[BaseModel]] | None = None,
    ) -> list[Response]:

        logger.info(f"Run method called with client type: {client}")
        output: list[Response] = []

        if context is None:
            context = {}

        if returns_model is None:
            returns_model = {}

        for k, v in returns_model.items():
            prompts[k].return_model = v
            prompts[k].prompt = (
                prompts[k].prompt
                + "\n\n Model schema: "
                + json.dumps(v.model_json_schema())
            )

        for prompt in prompts:
            for key, value in context.items():
                prompt.prompt = prompt.prompt.replace(f"{{{{{key}}}}}", str(value))

            for i, previous_output in enumerate(output):
                if isinstance(previous_output.response, dict):
                    prompt.prompt = prompt.prompt.replace(
                        f"{{{{output[-{len(output)-i}]}}}}",
                        json.dumps(previous_output.response),
                    )
                    for key, value in previous_output.response.items():
                        prompt.prompt = prompt.prompt.replace(
                            f"{{{{output[-{len(output)-i}].{key}}}}}", str(value)
                        )
                else:
                    prompt.prompt = prompt.prompt.replace(
                        f"{{{{output[-{len(output)-i}]}}}}",
                        str(previous_output.response),
                    )

            try:
                result = await self._handle_prompt(client, prompt, context)
                output.append(result)
            except APICallError as e:
                logger.error(f"Error in API call: {str(e)}")
                output.append(Response(response=f"Error: {str(e)}"))

        return output