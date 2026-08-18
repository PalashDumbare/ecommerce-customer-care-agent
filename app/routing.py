import re

from langchain_core.messages import AIMessage

from .state import CustomerCareState


def routing(state: CustomerCareState):
    # Whatever intent is present in the state becomes the routing decision.
    intent = state.get("intent", "")
    return intent if intent in {"order", "refund", "payment", "unknown"} else "unknown"


def route_agent(state: CustomerCareState):
    messages = state.get("messages", [])
    if not messages:
        return "end"
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "end"


def entry_router(state: CustomerCareState):
    if state.get("pending_confirmation", False):
        return "confirmation"

    messages = state.get("messages", [])
    if state.get("awaiting_order_id", False):
        text = str(messages[-1].content or "") if messages else ""
        if not re.search(r"\bORD\d+\b", text):
            return "understand_request"
        return "extract_order_id"
    return "understand_request"


def confirmation_router(state: CustomerCareState):
    messages = state.get("messages", [])
    if not messages:
        return "confirmation_unknown"

    message = str(messages[-1].content or "").strip().lower()

    if message in {"yes", "y", "yeah", "yep", "sure", "confirm", "proceed"}:
        return "confirm"

    if message in {"no", "n", "nope", "cancel", "don't", "do not"}:
        return "cancel"

    return "confirmation_unknown"
