import json
import random
import shutil
import requests
from pathlib import Path
from loguru import logger

from src.core.settings import Settings
from src.langg.state import ContentState
from src.utils.nodes import required_node, optional_node
from src.services.pchain.chainable import MinimalChainable
from src.services.localfile_service import LocalFileService
from src.services.elevenlabs_service import ElevenLabsService
from src.services.subtitle_generator import SubtitleGenerator
from src.services.pchain.chain_prompt_manager import ChainPromptManager
from src.langg.models import (
    ExceptionDict,
    ChooseStory,
    CheckStory,
    StoryContent,
    MidjourneyPrompts
)


class Nodes:
    def __init__(
        self,
        settings: Settings,
        chain_prompt_manager: ChainPromptManager,
        minimal_chainable: MinimalChainable,
        elevenlabs_service: ElevenLabsService,
        subtitle_generator: SubtitleGenerator,
        local_file_service: LocalFileService,
    ) -> None:
        self.settings = settings
        self.chain_prompt_manager = chain_prompt_manager
        self.minimal_chainable = minimal_chainable
        self.elevenlabs_service = elevenlabs_service
        self.subtitle_generator = subtitle_generator
        self.local_file_service = local_file_service

        self.mj_interactive_endpoint = f"{settings.MJ_INTERACTIVE_API}/generate_images"

    # @required_node()
    async def choose_story(self, state: ContentState):
        logger.info("Choosing story...")

        choose_story_prompts =  self.chain_prompt_manager.get_prompt_chain("choose_story")

        choose_story_responses = await self.minimal_chainable.run(
            prompts=choose_story_prompts,
            client="deepseek",
            model="deepseek-reasoner",
            context={
                "stories_done_list": state["stories_done"]
            }
        )

        parse_story_prompts =  self.chain_prompt_manager.get_prompt_chain("parse_output")
        parse_story_responses = await self.minimal_chainable.run(
            prompts=parse_story_prompts,
            client="deepseek",
            model="deepseek-chat",
            context={
                "input_string": choose_story_responses[0].response,
                "output_format": ChooseStory.model_json_schema()
            },
            returns_model={
                0: ChooseStory
            }
        )

        state["story_title"] = parse_story_responses[0].response.story_title
        state["story_carpet_name"] = parse_story_responses[0].response.carpet_name
        logger.info(f"Story chosen: {state['story_title']}")
        logger.info(f"Carpet name: {state['story_carpet_name']}")

        return state
    
    async def check_story(self, state: ContentState):
        logger.info("Checking story...")

        check_story_prompts =  self.chain_prompt_manager.get_prompt_chain("check_story")

        check_story_responses = await self.minimal_chainable.run(
            prompts=check_story_prompts,
            client="deepseek",
            model="deepseek-chat",
            context={
                "story_title": state["story_title"],
                "stories_done_list": state["stories_done"]
            },
            returns_model={
                0: CheckStory
            }
        )

        state["valid_story"] = not check_story_responses[0].response.is_story_done
        logger.info(f"Is a valid story? {state['valid_story']}")

        return state
    
    @required_node()
    def verify_path_and_create_folder(self, state: ContentState) -> ContentState:
        logger.info("Verifying path and creating folder...")
        if not self.local_file_service.is_valid_path(state["main_path"]):
            raise Exception(f"Path {state['main_path']} does not exist")
        
        folder_path = self.local_file_service.create_folder(state["main_path"], state['story_carpet_name'])
        if folder_path is None:
            raise Exception(f"Could not create folder {state['main_path']}/{state['story_carpet_name']}")
        
        state["folder_path"] = folder_path
        logger.info(f"Folder created: {folder_path}")

        return state
    
    # @required_node()
    async def get_story(self, state: ContentState):
        logger.info("Getting story content...")

        story_content_prompts = self.chain_prompt_manager.get_prompt_chain("get_story")
        story_content_responses = await self.minimal_chainable.run(
            prompts=story_content_prompts,
            model="deepseek-reasoner",
            client="deepseek",
            context={
                "story_name": state["story_title"]
            }
        )

        parse_story_prompts =  self.chain_prompt_manager.get_prompt_chain("parse_output")
        parse_story_responses = await self.minimal_chainable.run(
            prompts=parse_story_prompts,
            client="deepseek",
            model="deepseek-chat",
            context={
                "input_string": story_content_responses[0].response,
                "output_format": StoryContent.model_json_schema()
            },
            returns_model={
                0: StoryContent
            }
        )

        state["story_content"] = parse_story_responses[0].response.story_content_spanish
        logger.info("Got story content!")

        return state
    
    # @required_node()
    async def get_midjourney_prompts(self, state: ContentState):
        logger.info("Getting midjourney prompts...")

        midjourney_prompts = self.chain_prompt_manager.get_prompt_chain("get_midjourney_prompts")

        midjourney_prompts_responses = await self.minimal_chainable.run(
            prompts=midjourney_prompts,
            model="deepseek-chat",
            client="deepseek",
            context={
                "story": state["story_content"]
            },
            returns_model={
                0: MidjourneyPrompts
            }
        )

        state["midjourney_prompts"] = midjourney_prompts_responses[0].response.model_dump()["prompts"]
        logger.info("Got midjourney prompts!")

        return state
    
    @required_node()
    def get_mj_images(self, state: ContentState):
        logger.info("Getting midjourney images...")

        res = requests.post(
            url=self.mj_interactive_endpoint,
            json={
                "prompts_data": {
                    "directory": str(Path("temp").absolute()),
                    "img_prompts": state["midjourney_prompts"]
                },
                "encrypted_cookies": None,
                "key": None
            }
        )
        if res.status_code != 200:
            raise Exception(f"Error generating images: {res.text}")

        logger.info("Got midjourney images!")
        return state
    
    @required_node()
    def get_story_audio(self, state: ContentState):
        logger.info("Generating audio")

        voices = ["female", "male"]

        audio = self.elevenlabs_service.get_speech_on_file(
            filename=f"temp/{state['story_carpet_name']}.mp3",
            text=state["story_content"],
            voice=voices[random.randint(0, 1)]
        )

        state["audio_file"] = audio
        logger.info("Got story audio!")

        return state
    
    @optional_node()
    def get_subtitles(self, state: ContentState):
        logger.info("Generating subtitles")

        subtitles_file = self.subtitle_generator.get_subtitles(
            audio_file=state["audio_file"],
            str_name=state["story_carpet_name"],
            segment_type="word"
        )

        if subtitles_file is None:
            raise Exception("Could not generate subtitles")

        state["subtitles_file"] = subtitles_file
        logger.info("Got subtitles!")

        return state
    
    @required_node()
    def create_json(self, state: ContentState):
        logger.info("Creating json")

        if not self.local_file_service.create_empty_file(path="/temp",file_name="story.json"):
            raise Exception("Could not create json file")
        
        json_data = {
            "story_title": state["story_title"],
            "story_content": state["story_content"],
            "midjourney_prompts": state["midjourney_prompts"],
        }
        with open(f"temp/story.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False)

        state["json_file"] = "/temp/story.json"

        return state
    
    @required_node()
    def move_files(self, state: ContentState):
        logger.info("Moving files")

        if not self.local_file_service.move_all_files(src_folder="temp", dest_folder=state["folder_path"]):
            raise Exception("Could not move files")
        
        logger.info("Moved files!")

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
