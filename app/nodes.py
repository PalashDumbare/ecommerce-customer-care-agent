
from .state import CustomerCareState
from app.llm import intent_model

def understand_request(state: CustomerCareState):
    result = intent_model.invoke(state["message"])
    return {
        "intent": result["intent"]
    }


def handle_order(state: CustomerCareState):
    return {
        "response": "Sure! I can help you with your order."
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