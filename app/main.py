from .graph import graph
from .tools.order import get_order_status

def main():
    # messages = [
    #     "Where is my order?",
    #     "My delivery hasn't arrived yet",
    #     "I want my money back",
    #     "Where is my refund?",
    #     "You charged me twice",
    #     "My payment failed",
    #     "What is the weather today?",
    # ]


    result = graph.invoke(
        {
    "user_id": "U1001",
    "message": "where is my order?",
    "intent": "",
    "response": "",
    "order_id": "ORD1003",
}
    )

    print(f"\nUser: {result}")
    print(f"Intent: {result['intent']}")
    print(f"Response: {result['response']}")

if __name__ == "__main__":
    main()

