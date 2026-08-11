from typing_extensions import TypedDict
from typing import Literal,Annotated
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
    message: str
    intent: Intent
    response: str
    order_id : str
    messages : Annotated[list, add_messages]

# output we expect from the LLM
class IntentOutput(TypedDict):
    intent : Intent
