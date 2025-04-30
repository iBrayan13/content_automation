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
    carpet_name: str = Field(alias="carpet_name_es", description="This is the name of the carpet in Spanish, based on story_title use only three words.")

class CheckStory(BaseModel):
    story_title: str
    is_story_done: bool
    stories_done: list[str]


class StoryContent(BaseModel):
    story_title: str
    story_category: str
    story_content_english: str = Field(alias="story_content_en", description="This is the second story content in English. In Spanish the length is 160-220 words but in Englihs depends on the translation.")
    story_content_spanish: str = Field(alias="story_content_es", description="This is the official (main) story content in Spanish between 160-220 words.")
    recommend_narrator_genre: str

class MidjourneyPrompt(BaseModel):
    prompt_num: int
    prompt: str

class MidjourneyPrompts(BaseModel):
    prompts: list[MidjourneyPrompt]