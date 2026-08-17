
from .state import CustomerCareState
from app.llm import intent_model
from app.tools import get_order_status   
from app.llm import model_with_tools
from app.utils import print_latest_state
import re
from langchain_core.messages import ToolMessage
from app.tools.refund import submit_refund
import json

def agent(state : CustomerCareState):
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
            "For refund requests, always use the order ID and user ID "
            "provided above when calling the request_refund tool."
        ),
    }

    messages = [
        system_message,
        *state.get("messages", []),
    ]
    response = model_with_tools.invoke(messages)
    print_latest_state(state)
    update = {
        "messages" : [response]
    }

    # 1. LLM wants to call a tool
    if response.tool_calls:
        return update

    # 2. Check the previous message for a refund tool result
    last_message = state["messages"][-1]
    if (
        isinstance(last_message, ToolMessage)
        and last_message.name == "request_refund"
    ):
        result = json.loads(last_message.content)

        if result.get("found") and result.get("eligible"):
            update["pending_confirmation"] = True

    # 3. LLM needs the order ID
    if state.get("order_id") is None and state.get("intent") in {"order", "refund"}:
        update['response'] = response.content or ''
        update['awaiting_order_id'] = True
        return update

    # 4. Normal final response
    update["response"] = response.content or ""
    update["awaiting_order_id"] = False

    return update

def extract_order_id(state: CustomerCareState):
    message = state.get("messages", [])[-1].content

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
    message = state.get("messages", [])[-1].content

    result = intent_model.invoke(message)
    return {
        "intent": result["intent"],
        "awaiting_order_id" : False
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

    result = submit_refund.invoke({
        "order_id": state["order_id"],
        "user_id": state["user_id"],
    })
     
    if not result["success"]:
        return {
            "response": result["message"],
            "pending_confirmation": False,
        }

    return {
        "response": (
            f"Your refund request for order "
            f"{state['order_id']} has been submitted successfully."
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
        "response": "Please confirm whether you want to proceed with the refund by replying yes or no.",
        "pending_confirmation": True,
    }


def handle_confirmation_router(state: CustomerCareState):
    return {}