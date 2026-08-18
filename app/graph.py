"""Customer care LangGraph definition.

Responsibility separation (Phase 6):
    LLM    - understand intent, decide which read/tool operation is relevant,
             generate natural-language responses
    Graph  - manage workflow/state, multi-turn transitions, the confirmation
             workflow, and routing
    Tools  - validate inputs, authorize access, enforce business rules,
             perform reads/writes, and return structured results

Graph layout:
    START
      └─ entry_router ──┬─ understand_request ── routing ──┬─ agent (order/refund)
                        │                                  ├─ handle_payment
                        │                                  └─ handle_unknown
                        ├─ extract_order_id ── agent
                        └─ confirmation ── confirmation_router ──┬─ handle_confirmation
                                                                  ├─ handle_confirmation_cancel
                                                                  └─ handle_confirmation_unknown
    agent ── route_agent ──┬─ tools ── agent (loop for tool calls)
                           └─ END
    handle_payment / handle_unknown / handle_confirmation* ── END
"""

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

from app.tools.order import get_order_status
from app.tools.refund import request_refund
from .state import CustomerCareState
from .nodes import (
    understand_request,
    agent,
    extract_order_id,
    handle_payment,
    handle_unknown,
    handle_confirmation,
    handle_confirmation_cancel,
    handle_confirmation_unknown,
    handle_confirmation_router,
)
from .routing import routing, route_agent, entry_router, confirmation_router


# --- Tool node: lets the agent call the read/request tools only.
# submit_refund is deliberately NOT bound to the model: the refund write may
# only happen through the deterministic confirmation node. ---
tool_node = ToolNode([get_order_status, request_refund])

# --- Build the graph ---
builder = StateGraph(CustomerCareState)

# 1. Entry: pull the intent, or extract the order ID if we're still awaiting one.
builder.add_node("understand_request", understand_request)
builder.add_node("extract_order_id", extract_order_id)
builder.add_node("confirmation_router", handle_confirmation_router)
builder.add_conditional_edges(
    START,
    entry_router,
    {
       "understand_request": "understand_request",
       "extract_order_id": "extract_order_id",
       "confirmation": "confirmation_router",
    },
)
builder.add_edge("extract_order_id", "agent")
builder.add_conditional_edges(
    "confirmation_router",
    confirmation_router,
    {
        "confirm": "handle_confirmation",
        "cancel": "handle_confirmation_cancel",
        "confirmation_unknown": "handle_confirmation_unknown",
    },
)

# 2. Route the intent to the matching handler.
builder.add_node("agent", agent)
builder.add_node("tools", tool_node)
builder.add_node("handle_payment", handle_payment)
builder.add_node("handle_unknown", handle_unknown)

builder.add_node(
    "handle_confirmation",
    handle_confirmation
)

builder.add_node(
    "handle_confirmation_cancel",
    handle_confirmation_cancel
)

builder.add_node(
    "handle_confirmation_unknown",
    handle_confirmation_unknown
)

builder.add_conditional_edges(
    "understand_request",
    routing,
    {
        "order": "agent",
        "refund": "agent",
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
builder.add_edge("handle_payment", END)
builder.add_edge("handle_unknown", END)
builder.add_edge("handle_confirmation", END)
builder.add_edge("handle_confirmation_cancel", END)
builder.add_edge("handle_confirmation_unknown", END)

# --- Compile with an in-memory checkpointer for threaded conversations ---
graph = builder.compile(checkpointer=InMemorySaver())