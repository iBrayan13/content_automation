def check_story_edge(state):
    if state.get("end", False):
        return "end"
    elif not state.get("valid_story", False):
        return "retry_choose_story"
    else:
        return "verify_path_and_create_folder"