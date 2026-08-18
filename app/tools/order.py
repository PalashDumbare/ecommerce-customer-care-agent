from typing import Dict
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from .common import validate_order_id, validate_user_id, unexpected_error

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
    "ORD1004": {
        "order_id": "ORD1004",
        "user_id": "U1001",
        "status": "delivered",
        "estimated_delivery": None,
    },
}


@tool(
    description="""
        Get the status of an e-commerce order for the authenticated user.

        Use this when the customer asks about their order status,
        delivery status, or whether an order has been delivered.

        Validation and authorization are enforced automatically.
        """
)
def get_order_status(order_id: str, config: RunnableConfig) -> dict:

    order_id, err = validate_order_id(order_id)
    if err:
        return {"found": False, **err}

    user_id, err = validate_user_id((config or {}).get("configurable", {}).get("user_id"))
    if err:
        return {"found": False, **err}

    try:
        order = ORDERS.get(order_id)
    except Exception:
        return {"found": False, **unexpected_error("get_order_status")}

    if order is None or order["user_id"] != user_id:
        return {
            "found": False,
            "status": "not_found",
            "message": "Order not found.",
        }

    return {
        "found": True,
        "order": order,
    }
