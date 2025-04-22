from pydantic import BaseModel, Field

class GenerateInput(BaseModel):
    stories_done: list[str] = Field(description="List of stories already generated. (e.g. ['story_title_1', 'story_title_2', ...])")
    directory: str = Field(description="Complete path to the directory where the content will be saved. (e.g. C:/Users/Brayan/Desktop/content)")