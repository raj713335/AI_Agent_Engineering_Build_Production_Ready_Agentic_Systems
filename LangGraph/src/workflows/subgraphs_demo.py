from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class SubState(TypedDict):
    text: str


def sub_step(state: SubState):
    return {"text": "subgraph says: " + state["text"]}


sub_builder = StateGraph(SubState)

sub_builder.add_node("sub_step", sub_step)

sub_builder.add_edge(START, "sub_step")
sub_builder.add_edge("sub_step", END)

sub_graph = sub_builder.compile()


class ParentState(TypedDict):
    msg: str


def call_subgraph(state: ParentState):
    out = sub_graph.invoke({"text": state["msg"]})
    return {"msg": out["text"]}


parent = StateGraph(ParentState)

parent.add_node("call_subgraph", call_subgraph)

parent.add_edge(START, "call_subgraph")
parent.add_edge("call_subgraph", END)

graph = parent.compile()
print(graph.invoke({"msg": "hello world"}))
