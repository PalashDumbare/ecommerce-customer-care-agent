from typing_extensions import TypedDict

# state of the entire LangGraph
class CustomerCareState(TypedDict):
    user_id: str
    message: str
    intent: str
    response: str

# output we expect from the LLM
class IntentOutput(TypedDict):
    intent : str
