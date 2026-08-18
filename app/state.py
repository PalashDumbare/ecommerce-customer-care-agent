from typing import Literal, Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, NotRequired


Intent = Literal[
    "order",
    "refund",
    "payment",
    "unknown",
]


class CustomerCareState(TypedDict, total=False):
    """State of the whole conversation.

    Required at invocation time:
        user_id  - the authenticated user, set by the app layer (never the LLM)
        messages - the conversation history

    Optional fields, each with explicit transitions set by graph nodes:
        intent               - latest classified intent
        response             - the final user-facing response
        order_id             - validated order ID under discussion
        awaiting_order_id    - True while the agent is waiting for an order ID
        pending_confirmation - True while waiting for the refund confirmation
    """

    user_id: str
    intent: Intent
    response: NotRequired[str]
    order_id: NotRequired[str]
    awaiting_order_id: bool
    pending_confirmation: bool
    messages: Annotated[list, add_messages]


# structured output expected from the intent classifier
class IntentOutput(TypedDict):
    intent: Intent


def build_initial_state(user_id: str, message: str) -> dict:
    """Build the input state for a new turn.

    Only fields that are genuinely new for this turn are included: the
    authenticated user and the new user message. Workflow flags
    (awaiting_order_id, pending_confirmation, intent) are persisted in the
    checkpointer across turns and must NOT be reset here, or multi-turn
    routing would be broken. Their defaults live in the nodes via .get().
    """
    return {
        "user_id": user_id,
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ],
    }
