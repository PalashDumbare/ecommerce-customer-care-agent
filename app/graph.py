from langgraph.graph import StateGraph, START, END
from app.tools.order import get_order_status
from .state import CustomerCareState
from .nodes import (
    handle_payment,
    handle_refund,
    handle_unknown,
    understand_request,
    agent
)
from .routing import routing,route_agent
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(
    [
        get_order_status
    ]
)



builder = StateGraph(CustomerCareState)

builder.add_node("tools",tool_node)


builder.add_node("understand_request", understand_request)
builder.add_node("agent", agent)

builder.add_node("handle_refund", handle_refund)
builder.add_node("handle_payment", handle_payment)
builder.add_node("handle_unknown", handle_unknown)


builder.add_edge(START,"understand_request")


builder.add_conditional_edges(
    "understand_request",
    routing,
    {
        "order": "agent",
        "refund": "handle_refund",
        "payment": "handle_payment",
        "unknown": "handle_unknown",
    }
)

builder.add_edge("handle_refund", END)
builder.add_edge("handle_payment", END)
builder.add_edge("handle_unknown", END)


builder.add_conditional_edges(
    "agent",
    route_agent,
    {
        "tools": "tools",
        "end": END,
    }
)
builder.add_edge("tools", "agent")



graph = builder.compile()

