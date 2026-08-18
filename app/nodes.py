import json
import logging
import re

from langchain_core.messages import ToolMessage

from app.llm import intent_model
from app.llm import model_with_tools
from app.tools.refund import submit_refund

from .state import CustomerCareState

logger = logging.getLogger(__name__)


def agent(state: CustomerCareState):
    if (
        state.get("order_id") is None
        and state.get("intent") in {"order", "refund"}
    ):
        return {
            "response": "Please provide your order ID.",
            "awaiting_order_id": True,
        }

    system_message = {
        "role": "system",
        "content": (
            "You are an e-commerce customer care agent. "
            "Help the customer with their request. "
            f"The authenticated user ID is {state.get('user_id', '')}. "
            f"The relevant order ID is {state.get('order_id', '')}. "
            "You have two tools available: get_order_status for checking "
            "an order's delivery status, and request_refund for handling "
            "refund requests or questions about refund status. "
            "Call a tool with the order ID only; the authenticated user "
            "is enforced automatically by the system. "
            "If a tool reports that an order was not found or that an "
            "operation failed, tell the customer helpfully. Never guess "
            "or invent order details."
        ),
    }

    messages = [
        system_message,
        *state.get("messages", []),
    ]

    try:
        response = model_with_tools.invoke(messages)
    except Exception:
        logger.error("Agent LLM call failed", exc_info=True)
        return {
            "response": "I'm having trouble right now. Please try again in a moment.",
            "awaiting_order_id": state.get("awaiting_order_id", False),
        }

    update = {
        "messages": [response],
    }

    # 1. LLM wants to call a tool
    if response.tool_calls:
        return update

    # 2. A completed request_refund with an eligible, not-yet-requested
    #    order moves the conversation into the confirmation workflow.
    messages_so_far = state.get("messages", [])
    last_message = messages_so_far[-1] if messages_so_far else None
    if (
        isinstance(last_message, ToolMessage)
        and last_message.name == "request_refund"
    ):
        try:
            result = json.loads(last_message.content)
        except (TypeError, ValueError):
            logger.warning("Unparseable tool message: %r", last_message.content)
            result = {}
        if (
            result.get("found")
            and result.get("eligible")
            and result.get("status") == "not_requested"
        ):
            update["pending_confirmation"] = True

    # 3. LLM still needs the order ID
    if state.get("order_id") is None and state.get("intent") in {"order", "refund"}:
        update["response"] = response.content or ""
        update["awaiting_order_id"] = True
        return update

    # 4. Normal final response
    update["response"] = response.content or ""
    update["awaiting_order_id"] = False

    return update


def extract_order_id(state: CustomerCareState):
    messages = state.get("messages", [])
    if not messages:
        return {
            "response": "Please provide a valid order ID, such as ORD1001.",
            "awaiting_order_id": True,
        }

    message = str(messages[-1].content or "")

    match = re.search(
        r"\bORD\d+\b",
        message.upper()
    )

    if not match:
        return {
            "response": "Please provide a valid order ID, such as ORD1001.",
            "awaiting_order_id": True,
        }

    order_id = match.group(0)

    return {
        "order_id": order_id,
        "awaiting_order_id": False,
    }


def understand_request(state: CustomerCareState):
    messages = state.get("messages", [])
    if not messages:
        return {
            "intent": "unknown",
            "awaiting_order_id": False,
        }

    message = str(messages[-1].content or "")

    result = intent_model.invoke(message)
    return {
        "intent": result["intent"],
        "awaiting_order_id": False,
    }


def handle_payment(state: CustomerCareState):
    return {
        "response": "I can help you with your payment-related concerns."
    }


def handle_unknown(state: CustomerCareState):
    return {
        "response": "Could you provide more details about your issue?"
    }


def handle_confirmation(state: CustomerCareState):
    # Confirmation safety: only a valid, pending confirmation may submit.
    # This node (not the LLM) deterministically executes the write.
    if not state.get("pending_confirmation", False):
        return {
            "response": "Refund requests must be confirmed before submission.",
            "pending_confirmation": False,
        }

    result = submit_refund.invoke(
        {"order_id": state.get("order_id")},
        config={"configurable": {"user_id": state.get("user_id")}},
    )

    if not result["success"]:
        return {
            "response": result["message"],
            "pending_confirmation": False,
        }

    return {
        "response": (
            f"Your refund request for order {state['order_id']} "
            "has been submitted successfully."
        ),
        "pending_confirmation": False,
    }


def handle_confirmation_cancel(state: CustomerCareState):
    return {
        "response": "No problem. I won't proceed with the refund.",
        "pending_confirmation": False,
    }


def handle_confirmation_unknown(state: CustomerCareState):
    return {
        "response": (
            "Please confirm whether you want to proceed with the "
            "refund by replying yes or no."
        ),
        "pending_confirmation": True,
    }


def handle_confirmation_router(state: CustomerCareState):
    return {}
