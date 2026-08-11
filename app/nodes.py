
from .state import CustomerCareState
from app.llm import intent_model
from app.tools import get_order_status   
from app.llm import model_with_tools


def understand_request(state: CustomerCareState):
    result = intent_model.invoke(state["message"])
    print(f"Response from the LLM : {result}")
    return {
        "intent": result["intent"]
    }


def agent(state : CustomerCareState):
    print("In the agent")

    system_message = {
        "role": "system",
        "content": (
            "You are an e-commerce customer care agent. "
            "Help the customer with their request. "
            f"The authenticated user ID is {state['user_id']}. "
            f"The relevant order ID is {state['order_id']}."
        ),
    }

    messages = [
        system_message,
        *state["messages"],
    ]

    print(f"PROMPT TO THE AGENT {messages}")
    response = model_with_tools.invoke(messages)

    update = {
        "messages" : [response]
    }

    if not response.tool_calls:
        update["response"] = response.content

    return update

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