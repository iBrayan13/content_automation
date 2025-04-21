from langgraph.graph import END, StateGraph, graph

from src.langg.nodes import Nodes


class WorkFlow:
    def __init__(self, nodes: Nodes, state_graph: StateGraph):
        self.nodes = nodes
        self.workflow_app = state_graph
        self.app: graph.CompiledGraph

        self._compile_workflow()

    def _compile_workflow(self):

        # NODES
        self.workflow_app.add_node("choose_story", self.nodes.choose_story)
        self.workflow_app.add_node("get_story", self.nodes.get_story)
        self.workflow_app.add_node("get_midjourney_prompts", self.nodes.get_midjourney_prompts)
        self.workflow_app.add_node("clean_up_temp", self.nodes.clean_up_node)

        self.workflow_app.add_conditional_edges(
            "choose_story",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "get_story"},
        )
        self.workflow_app.add_conditional_edges(
            "get_story",
            lambda x: x.get("end", False),
            {True: "clean_up_temp", False: "get_midjourney_prompts"},
        )
        
        self.workflow_app.add_edge("get_midjourney_prompts", "clean_up_temp")
        self.workflow_app.add_edge("clean_up_temp", END)

        self.workflow_app.set_entry_point("choose_story")

        self.app = self.workflow_app.compile()