
from .state import CustomerCareState
from app.llm import intent_model
from app.tools import get_order_status   
from app.llm import model_with_tools
import re


def understand_request(state: CustomerCareState):
    message = state.get("messages", [])[-1].content

    result = intent_model.invoke(message)
    return {
        "intent": result["intent"]
    }


def agent(state : CustomerCareState):
    system_message = {
        "role": "system",
        "content": (
            "You are an e-commerce customer care agent. "
            "Help the customer with their request. "
            f"The authenticated user ID is {state.get('user_id', '')}. "
            f"The relevant order ID is {state.get('order_id', '')}."
        ),
    }

    messages = [
        system_message,
        *state.get("messages", []),
    ]
    response = model_with_tools.invoke(messages)
    update = {
        "messages" : [response]
    }

    # 1. LLM wants to call a tool
    if response.tool_calls:
        return update

    # 2. LLM needs the order ID
    if not state.get("order_id") and state.get("intent", "") == "order":
        update['response'] = response.content or ''
        update['awaiting_order_id'] = True
        return update

    # 3. Normal final response
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


def handle_refund(state: CustomerCareState):
    return {
        "response": "I can assist you with your refund request."
    }

def handle_payment(state: CustomerCareState):
    return {
        "response": "I can help you with your payment-related concerns."
    }

def handle_unknown(state: CustomerCareState):
    return {
        "response": "Could you provide more details about your issue?"
    }