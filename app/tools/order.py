from typing import Dict
from langchain_core.tools import tool

ORDERS: Dict[str, dict] = {
    "ORD1001": {
        "order_id": "ORD1001",
        "user_id": "U1001",
        "status": "out_for_delivery",
        "estimated_delivery": "20 minutes",
    },
    "ORD1002": {
        "order_id": "ORD1002",
        "user_id": "U1001",
        "status": "delivered",
        "estimated_delivery": None,
    },
    "ORD1003": {
        "order_id": "ORD1003",
        "user_id": "U1002",
        "status": "cancelled",
        "estimated_delivery": None,
    },
}

@tool(
    description= """
        Get the status of an e-commerce order for a user.
    
        Use this when the customer asks about their order status,
        delivery status, or whether an order has been delivered.
        """
)
def get_order_status(order_id, user_id):

    order = ORDERS.get(order_id)

    if order is None:
        return {
            "found" : False,
            "message" : "order not found"
        }

    if order["user_id"] != user_id:
        return {
            "found" : False,
            "message" : "order not found" 
        }

    return {
        "found": True,
        "order": order,
    }