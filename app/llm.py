from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from app.state import IntentOutput

intent_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an intent classifier for an e-commerce customer care system.

Classify the customer's message into exactly one of these intents:

- order: order status, delivery, cancellation, or order-related issues
- refund: refund requests or refund status
- payment: payment failures, duplicate charges, or payment issues
- unknown: anything that does not clearly belong to the above categories

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

intent_model = (intent_prompt | model.with_structured_output(IntentOutput))

