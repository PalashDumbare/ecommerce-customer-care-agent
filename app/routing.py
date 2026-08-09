
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