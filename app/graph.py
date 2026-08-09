from langgraph.graph import StateGraph, START, END

from .state import CustomerCareState
from .nodes import (
    handle_order,
    handle_payment,
    handle_refund,
    handle_unknown,
    understand_request,
)
from .routing import routing

builder = StateGraph(CustomerCareState)

builder.add_node("understand_request", understand_request)
builder.add_node("handle_order", handle_order)
builder.add_node("handle_refund", handle_refund)
builder.add_node("handle_payment", handle_payment)
builder.add_node("handle_unknown", handle_unknown)


builder.add_edge(START,"understand_request")


builder.add_conditional_edges(
    "understand_request",
    routing,
    {
        "order": "handle_order",
        "refund": "handle_refund",
        "payment": "handle_payment",
        "unknown": "handle_unknown",
    }
)

builder.add_edge("handle_order", END)
builder.add_edge("handle_refund", END)
builder.add_edge("handle_payment", END)
builder.add_edge("handle_unknown", END)


graph = builder.compile()

