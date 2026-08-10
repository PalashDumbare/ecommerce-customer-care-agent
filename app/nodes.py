
from .state import CustomerCareState
from app.llm import intent_model
from app.tools import get_order_status   

def understand_request(state: CustomerCareState):
    result = intent_model.invoke(state["message"])
    print(f"Response from the LLM : {result}")
    return {
        "intent": result["intent"]
    }


def handle_order(state: CustomerCareState):
    result = get_order_status(
        state["order_id"],
        state["user_id"]
    )
    if not result["found"]:
        return {
            "response" : "Could'nt found the order"
        }
    order = result["order"]
    return {
        "response" : (
            f"Your Order {order['order_id']} is "
            f"{order['status'].replace('-',' ')}. "
            f"Estimated delivery : {order['estimated_delivery']}"
        )
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