import logging

from fastapi import APIRouter, Depends, status

from src.langg.nodes import Nodes
from src.langg.graph import WorkFlow
from src.langg.graph import StateGraph
from src.core.settings import Settings
from src.langg.state import ContentState
from src.models.content import GenerateInput
from src.services.pchain.chainable import MinimalChainable
from src.services.localfile_service import LocalFileService
from src.services.elevenlabs_service import ElevenLabsService
from src.services.subtitle_generator import SubtitleGenerator
from src.services.pchain.chain_prompt_manager import ChainPromptManager

logger = logging.getLogger(__name__)

content_router = APIRouter(tags=["content"], prefix="/content")


@content_router.post(
    "/generate",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "",
            "content": {
                "application/json": {"example": {}}
            },
        },
    },
)
async def generate_content(body: GenerateInput):
    logger.info("Generate Content request received!")
    settings = Settings()
    chain_prompt_manager = ChainPromptManager()
    minimal_chainable = MinimalChainable(settings)
    local_file_service = LocalFileService()
    elevenlabs_service = ElevenLabsService(settings)
    subtitle_generator = SubtitleGenerator()

    nodes = Nodes(
        settings=settings,
        chain_prompt_manager=chain_prompt_manager,
        minimal_chainable=minimal_chainable,
        elevenlabs_service=elevenlabs_service,
        subtitle_generator=subtitle_generator,
        local_file_service=local_file_service,
    )
    workflow = WorkFlow(nodes, StateGraph(ContentState))
    output = await workflow.app.ainvoke(input={"stories_done": body.stories_done, "main_path": body.directory})

    return {
        "message": "Success. Content generated on directory destiny successfully!",
        "data": {
            "story_title": output["story_title"],
            "story_content": output["story_content"],
            "midjourney_prompts": output["midjourney_prompts"],
        }
    }