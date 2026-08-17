from typing_extensions import TypedDict
from typing import Literal,Annotated,Optional
from langgraph.graph.message import add_messages


Intent = Literal[
    "order",
    "refund",
    "payment",
    "unknown",
]

# state of the entire LangGraph
class CustomerCareState(TypedDict):
    user_id: str
    intent: Intent
    response: str
    order_id : Optional[str]
    awaiting_order_id: bool
    pending_confirmation: bool
    messages : Annotated[list, add_messages]

# output we expect from the LLM
class IntentOutput(TypedDict):
    intent : Intent
