# ecommerce-customer-care-agent

An intent-based customer care agent built with [LangGraph](https://langchain-ai.github.io/langgraph/) and [Ollama](https://ollama.com/).

## How it works

The agent classifies each customer message into an intent and routes it to the appropriate handler:

1. `understand_request` — classifies the customer's message using the LLM.
2. Routing — picks the handler based on the detected intent.
3. `handle_order` / `handle_refund` / `handle_payment` / `handle_unknown` — respond accordingly.

```
START → understand_request → (order | refund | payment | unknown) → END
```

Supported intents:

| Intent | Meaning |
| ------ | ------- |
| `order` | Order status, delivery, cancellation |
| `refund` | Refund requests and status |
| `payment` | Payment failures, duplicate charges |
| `unknown` | Anything not clearly classified |

## Requirements

- Python 3.x
- [Ollama](https://ollama.com/) running locally with the `qwen3:latest` model pulled (`ollama pull qwen3:latest`)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The current `main()` invocation in `app/main.py` sends a sample message and prints the full graph result.
