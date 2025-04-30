from typing_extensions import TypedDict, List, Dict, Any

class ContentState(TypedDict):
    main_path: str
    stories_done: List[str]
    story_title: str
    story_carpet_name: str
    valid_story: bool
    folder_path: str
    story_content: str
    midjourney_prompts: List[Dict[str, Any]]
    audio_file: str
    json_file: str