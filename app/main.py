from .graph import graph

def main():
    messages = [
        "Where is my order?",
        "My delivery hasn't arrived yet",
        "I want my money back",
        "Where is my refund?",
        "You charged me twice",
        "My payment failed",
        "What is the weather today?",
    ]

    for message in messages:

        result = graph.invoke({
            "user_id": "U1001",
            "message": message,
            "intent": "",
            "response": "",
        })

        print(f"\nUser: {message}")
        print(f"Intent: {result['intent']}")
        print(f"Response: {result['response']}")


if __name__ == "__main__":
    main()

