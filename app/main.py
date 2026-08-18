import logging

from app.graph import graph
from app.state import build_initial_state

# Show application logs (e.g. tool error handling) but keep the noisy
# HTTP client loggers quiet.
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def main():

    config = {
        "configurable": {
            "thread_id": "conversation-1005",
            "user_id": "U1002",
        }
    }

    print("Customer Care Agent")
    print("Type 'quit' to exit.\n")

    while True:

        message = input("You: ")

        if not message:
            continue

        if message.lower() == "quit":
            print("Goodbye!")
            break

        prompt = build_initial_state("U1002", message)
        result = graph.invoke(
            prompt,
            config=config,
        )

        print(f"Agent: {result['response']}\n")


if __name__ == "__main__":
    main()