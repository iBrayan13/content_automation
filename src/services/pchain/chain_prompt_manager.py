import json
import os
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr


class ClientPrompt(BaseModel):
    prompt: str
    content_keys: list[str] = Field(default_factory=list)
    return_model: type[BaseModel] | None = None


class ChainPromptManager(BaseModel):
    _storage_dir: str = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        self._storage_dir = os.path.abspath("src/services/pchain/prompt_chains")
        os.makedirs(self._storage_dir, exist_ok=True)

    def _get_file_path(self, name: str, chain_type: str) -> str:
        return os.path.join(self._storage_dir, f"{chain_type}_{name}.json")

    def add_prompt_chain(self, name: str, prompts: list[ClientPrompt]) -> None:
        file_path = self._get_file_path(name, "prompt")

        data = {
            "prompts": [
                {
                    "prompt": prompt.prompt,
                    "content_keys": prompt.content_keys,
                    "return_model": None,
                }
                for prompt in prompts
            ]
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_prompt_chain(self, name: str) -> list[ClientPrompt]:
        file_path = self._get_file_path(name, "prompt")
        logger.info(f"Looking for prompt chain file: {file_path}")
        if os.path.exists(file_path):
            with open(file_path) as f:
                data = json.load(f)
            prompts = [ClientPrompt(**prompt) for prompt in data.get("prompts", [])]
            return prompts
        else:
            logger.info(f"File not found: {file_path}")
        return []