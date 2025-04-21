from pydantic import BaseModel

class GenerateInput(BaseModel):
    stories_done: list[str]