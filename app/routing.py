
from .state import CustomerCareState

def routing(state: CustomerCareState):
    # Whatever intent is present in the state becomes the routing decision.
    #
        #intent = "order"
        #    ↓
        # route_intent()
        #    ↓
        # "order"
   intent = state["intent"]
   return intent if intent in {"order", "refund", "payment", "unknown"} else "unknown"


def route_agent(state : CustomerCareState):
   last_message = state['messages'][-1]
   if last_message.tool_calls:
      return "tools"
   return "end"