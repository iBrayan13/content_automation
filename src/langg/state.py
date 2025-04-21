from typing_extensions import TypedDict, List, Dict, Any

class ContentState(TypedDict):
    stories_done: List[str]
    story_title: str
    story_content: str
    midjourney_prompts: List[Dict[str, Any]]