"""Customer care LangGraph definition.

Graph layout:
    START
      └─ entry_router ──┬─ understand_request ── routing ──┬─ agent (order)
                        │                                  ├─ handle_refund
                        └─ extract_order_id ── agent       ├─ handle_payment
                                                        └─ handle_unknown
    agent ── route_agent ──┬─ tools ── agent (loop for tool calls)
                           └─ END
"""

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

from app.tools.order import get_order_status
from .state import CustomerCareState
from .nodes import (
    understand_request,
    agent,
    extract_order_id,
    handle_refund,
    handle_payment,
    handle_unknown,
)
from .routing import routing, route_agent, entry_router


# --- Tool node: lets the agent call the order-status tool ---
tool_node = ToolNode([get_order_status])

# --- Build the graph ---
builder = StateGraph(CustomerCareState)

# 1. Entry: pull the intent, or extract the order ID if we're still awaiting one.
builder.add_node("understand_request", understand_request)
builder.add_node("extract_order_id", extract_order_id)
builder.add_conditional_edges(
    START,
    entry_router,
    {
        "understand_request": "understand_request",
        "extract_order_id": "extract_order_id",
    },
)
builder.add_edge("extract_order_id", "agent")

# 2. Route the intent to the matching handler.
builder.add_node("agent", agent)
builder.add_node("tools", tool_node)
builder.add_node("handle_refund", handle_refund)
builder.add_node("handle_payment", handle_payment)
builder.add_node("handle_unknown", handle_unknown)
builder.add_conditional_edges(
    "understand_request",
    routing,
    {
        "order": "agent",
        "refund": "handle_refund",
        "payment": "handle_payment",
        "unknown": "handle_unknown",
    },
)

# 3. Agent loop: keep calling tools until a final answer is produced.
builder.add_conditional_edges(
    "agent",
    route_agent,
    {
        "tools": "tools",
        "end": END,
    },
)
builder.add_edge("tools", "agent")

# 4. Simple handlers terminate the conversation directly.
builder.add_edge("handle_refund", END)
builder.add_edge("handle_payment", END)
builder.add_edge("handle_unknown", END)

# --- Compile with an in-memory checkpointer for threaded conversations ---
graph = builder.compile(checkpointer=InMemorySaver())