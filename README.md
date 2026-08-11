# ecommerce-customer-care-agent

An intent-based customer care agent built with [LangGraph](https://langchain-ai.github.io/langgraph/) and [Ollama](https://ollama.com/).

## How it works

The agent classifies each customer message into an intent and routes it to the appropriate handler. Order-related queries are handled by an LLM agent that can call tools to look up order data.

1. `understand_request` — classifies the customer's message using the LLM.
2. Routing — picks the handler based on the detected intent.
3. `agent` — handles order queries; it can call the `get_order_status` tool, looping between the agent and the `ToolNode` until it produces a final answer.
4. `handle_refund` / `handle_payment` / `handle_unknown` — respond to the remaining intents.

```
START → understand_request → (agent | handle_refund | handle_payment | handle_unknown) → END

       agent → [has tool calls?] → tools → agent
              └── no tool calls ──→ END
```

## Tools

| Tool | Description |
| ---- | ----------- |
| `get_order_status` | Looks up the status, delivery estimate, and owner of an order by `order_id` / `user_id`. |

## Supported intents

| Intent | Meaning |
| ------ | ------- |
| `order` | Order status, delivery, cancellation (handled by the agent + tools) |
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

## Project layout

```
customer_care/
├── main.py              # entry point
└── app/
    ├── graph.py         # StateGraph construction & compile
    ├── state.py         # state definitions (CustomerCareState, IntentOutput)
    ├── nodes.py         # graph node functions
    ├── routing.py       # conditional routing logic
    ├── llm.py           # Ollama model + intent classifier
    ├── main.py          # sample invocation
    └── tools/
        ├── order.py     # get_order_status tool + sample order data
        └── __init__.py
```
