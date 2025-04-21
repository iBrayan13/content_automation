import time
import random
import shutil
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.core.settings import Settings
from src.langg.state import ContentState
from src.utils.nodes import required_node, optional_node
from src.services.pchain.chainable import MinimalChainable
from src.services.elevenlabs_service import ElevenLabsService
from src.services.pchain.chain_prompt_manager import ChainPromptManager
from src.langg.models import (
    ExceptionDict,
    ChooseStory,
    StoryContent,
    MidjourneyPrompts
)

logger = logging.getLogger(__name__)

class Nodes:
    def __init__(
        self,
        settings: Settings,
        chain_prompt_manager: ChainPromptManager,
        minimal_chainable: MinimalChainable,
        elevenlabs_service: ElevenLabsService
    ) -> None:
        self.settings = settings
        self.chain_prompt_manager = chain_prompt_manager
        self.minimal_chainable = minimal_chainable
        self.elevenlabs_service = elevenlabs_service

    # @required_node()
    async def choose_story(self, state: ContentState):

        choose_story_prompts =  self.chain_prompt_manager.get_prompt_chain("choose_story")

        choose_story_responses = await self.minimal_chainable.run(
            prompts=choose_story_prompts,
            client="deepseek",
            context={
                "stories_done_list": state["stories_done"]
            },
            returns_model={
                0: ChooseStory
            }
        )

        state["story_title"] = choose_story_responses[0].response.story_title

        return state
    
    # @required_node()
    async def get_story(self, state: ContentState):

        story_content_prompts = self.chain_prompt_manager.get_prompt_chain("get_story")

        story_content_responses = await self.minimal_chainable.run(
            prompts=story_content_prompts,
            client="deepseek",
            context={
                "story_name": state["story_title"]
            },
            returns_model={
                0: StoryContent
            }
        )

        state["story_content"] = story_content_responses[0].response.story_content_spanish

        return state
    
    # @required_node()
    async def get_midjourney_prompts(self, state: ContentState):

        midjourney_prompts = self.chain_prompt_manager.get_prompt_chain("get_story")

        midjourney_prompts_responses = await self.minimal_chainable.run(
            prompts=midjourney_prompts,
            client="deepseek",
            context={
                "story": state["story_content"]
            },
            returns_model={
                0: MidjourneyPrompts
            }
        )

        state["midjourney_prompts"] = midjourney_prompts_responses[0].response.model_dump()["prompts"]

        return state

    def clean_up_node(self, state: ContentState):
        logger.info("Cleaning up")
        temp_path = Path("temp")

        for f in temp_path.glob("*"):
            if f.is_dir():
                shutil.rmtree(f)
            elif f.is_file():
                f.unlink()

        return state
