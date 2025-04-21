import logging

from fastapi import APIRouter, Depends, status

from src.langg.nodes import Nodes
from src.langg.graph import WorkFlow
from src.langg.graph import StateGraph
from src.core.settings import Settings
from src.langg.state import ContentState
from src.models.content import GenerateInput
from src.services.pchain.chainable import MinimalChainable
from src.services.elevenlabs_service import ElevenLabsService
from src.services.pchain.chain_prompt_manager import ChainPromptManager

logger = logging.getLogger(__name__)

content_router = APIRouter(tags=["content"], prefix="/content")


@content_router.get(
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
    elevenlabs_service = ElevenLabsService(settings)

    nodes = Nodes(
        settings=settings,
        chain_prompt_manager=chain_prompt_manager,
        minimal_chainable=minimal_chainable,
        elevenlabs_service=elevenlabs_service
    )
    workflow = WorkFlow(nodes, StateGraph(ContentState))
    output = await workflow.app.ainvoke(input={"stories_done": body.stories_done})

    return {
        "message": "Success",
        "data": {
            "story_title": output["story_title"],
            "story_content": output["story_content"],
            "midjourney_prompts": output["midjourney_prompts"],
            "story_audio": output["audio_file"],
        }
    }