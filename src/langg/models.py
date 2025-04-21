from typing_extensions import TypedDict
from pydantic import BaseModel, Field, field_validator

class ExceptionDict(TypedDict):
    exception_node: str
    exception_type: str
    exception_text: SyntaxWarning
    end: bool

class ChooseStory(BaseModel):
    story_title: str
    reason: str
    story_category: str
    recommend_narrator_genre: str

class StoryContent(BaseModel):
    story_title: str
    story_category: str
    story_content_english: str
    story_content_spanish: str
    recommend_narrator_genre: str

class MidjourneyPrompt(BaseModel):
    prompt_num: int
    prompt: str

class MidjourneyPrompts(BaseModel):
    prompts: list[MidjourneyPrompt]