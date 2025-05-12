from langgraph.graph import END, StateGraph, graph

from src.langg.nodes import Nodes
from src.utils.graph import check_story_edge

class WorkFlow:
    def __init__(self, nodes: Nodes, state_graph: StateGraph):
        self.nodes = nodes
        self.workflow_app = state_graph
        self.app: graph.CompiledGraph

        self._compile_workflow()

    def _compile_workflow(self):

        # NODES
        self.workflow_app.add_node("choose_story", self.nodes.choose_story)
        self.workflow_app.add_node("check_story", self.nodes.check_story)
        self.workflow_app.add_node("verify_path_and_create_folder", self.nodes.verify_path_and_create_folder)
        self.workflow_app.add_node("get_story", self.nodes.get_story)
        self.workflow_app.add_node("get_midjourney_prompts", self.nodes.get_midjourney_prompts)
        self.workflow_app.add_node("get_mj_images", self.nodes.get_mj_images)
        self.workflow_app.add_node("get_story_audio", self.nodes.get_story_audio)
        self.workflow_app.add_node("get_subtitles", self.nodes.get_subtitles)
        self.workflow_app.add_node("create_json", self.nodes.create_json)
        self.workflow_app.add_node("move_files", self.nodes.move_files)
        self.workflow_app.add_node("clean_up_temp", self.nodes.clean_up_node)

        # EDGES
        self.workflow_app.add_conditional_edges(
            "choose_story",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "check_story"},
        )
        self.workflow_app.add_conditional_edges(
            "check_story",
            check_story_edge,
            {
                "end": "clean_up_temp",
                "retry_choose_story": "choose_story",
                "verify_path_and_create_folder": "verify_path_and_create_folder"
            },
        )
        self.workflow_app.add_conditional_edges(
            "verify_path_and_create_folder",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "get_story"},
        )
        self.workflow_app.add_conditional_edges(
            "get_story",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "get_midjourney_prompts"},
        )
        self.workflow_app.add_conditional_edges(
            "get_midjourney_prompts",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "get_mj_images"},
        )
        self.workflow_app.add_conditional_edges(
            "get_mj_images",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "get_story_audio"},
        )
        self.workflow_app.add_conditional_edges(
            "get_story_audio",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "get_subtitles"},
        )
        self.workflow_app.add_conditional_edges(
            "get_subtitles",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "create_json"},
        )
        self.workflow_app.add_conditional_edges(
            "create_json",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "move_files"},
        )
        
        self.workflow_app.add_edge("move_files", "clean_up_temp")
        self.workflow_app.add_edge("clean_up_temp", END)

        self.workflow_app.set_entry_point("choose_story")

        self.app = self.workflow_app.compile()