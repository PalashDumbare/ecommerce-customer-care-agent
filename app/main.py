from .graph import graph

def main():
    result = graph.invoke(
        {
            "user_id": "U1001",
            "message": "What's the weather today?",
            "intent": "",
            "response": "",
        }
    )
    print(f"result = {result}")


