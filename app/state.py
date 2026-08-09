from typing_extensions import TypedDict
from typing import Literal

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

# output we expect from the LLM
class IntentOutput(TypedDict):
    intent : Intent
