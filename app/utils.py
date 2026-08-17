import json


def print_latest_state(state):
    print("\n=== Latest State ===")
    print(json.dumps(state, indent=2, default=str))
    print("====================\n")