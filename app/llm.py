from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from app.state import IntentOutput
from app.tools import get_order_status

intent_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an intent classifier for an e-commerce
customer care system.

Classify the customer's message into exactly one
of these intents.

order:
Questions or problems related to an existing order,
including delivery status, delayed delivery,
missing order, or order cancellation.

refund:
Requests for a refund or questions about refund status.

payment:
Payment failures, duplicate charges, incorrect charges,
or other payment-related problems.

unknown:
Anything that does not clearly belong to the
above categories.

Return only the structured intent.
"""
    ),
    (
        "human",
        "{message}"
    ),
])

model = ChatOllama(
    model= "qwen3:latest",
    temperature=0 # no creative variation.
)

model_with_tools = model.bind_tools(
    [
        get_order_status
    ]
)

# model -> classification
intent_model = (intent_prompt | model.with_structured_output(IntentOutput))

