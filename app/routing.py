
from .state import CustomerCareState
import re
from langchain_core.messages import AIMessage

def routing(state: CustomerCareState):
    # Whatever intent is present in the state becomes the routing decision.
    #
        #intent = "order"
        #    ↓
        # route_intent()
        #    ↓
        # "order"
   intent = state.get("intent", "")
   return intent if intent in {"order", "refund", "payment", "unknown"} else "unknown"


def route_agent(state : CustomerCareState):
   last_message = state.get("messages", [])[-1]
   if isinstance(last_message, AIMessage) and last_message.tool_calls:
      return "tools"
   return "end"

def entry_router(state: CustomerCareState):
    if state.get("pending_confirmation", False):
        return "confirmation"
    
    if state.get('awaiting_order_id',False) == True:

      match = re.search(
         r"\bORD\d+\b",
         state.get("messages")[-1].content
      )
      if not match:
         return "understand_request"
      return "extract_order_id"
    else: 
      return "understand_request"


def confirmation_router(state: CustomerCareState):

    message = state["messages"][-1].content.strip().lower()

    if message in {"yes", "y", "yeah", "yep", "sure", "confirm", "proceed"}:
        return "confirm"

    if message in {"no", "n", "nope", "cancel", "don't", "do not"}:
        return "cancel"

    return "confirmation_unknown"
