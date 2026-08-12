from app.graph import graph


def main():

    config = {
        "configurable": {
            "thread_id": "conversation-1001"
        }
    }

    print("Customer Care Agent")
    print("Type 'quit' to exit.\n")

    while True:

        message = input("You: ")

        if message.lower() == "quit":
            print("Goodbye!")
            break

        prompt =  {
                "user_id": "U1002",
                "message": message,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
            }
        result = graph.invoke(
            prompt,
            config=config,
        )

        print(f"Agent: {result['response']}\n")


if __name__ == "__main__":
    main()