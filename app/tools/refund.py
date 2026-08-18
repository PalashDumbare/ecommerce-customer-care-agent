from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from app.tools.order import ORDERS
from .common import validate_order_id, validate_user_id, unexpected_error

REFUNDS = {
    "ORD1001": {
        "eligible": True,
        "status": "not_requested",
    },
    "ORD1002": {
        "eligible": False,
        "status": "already_refunded",
    },
    "ORD1003": {
        "eligible": True,
        "status": "not_requested",
    },
    "ORD1004": {
        "eligible": False,
        "status": "not_eligible",
    },
}


@tool(
    description="""
        Request a refund for the authenticated user's order,
        or check the status of a refund for the authenticated user.

        Use this when the customer asks for a refund or
        asks about the status of an existing refund.

        Validation and authorization are enforced automatically.
        """
)
def request_refund(order_id: str, config: RunnableConfig) -> dict:

    order_id, err = validate_order_id(order_id)
    if err:
        return {"found": False, **err}

    user_id, err = validate_user_id((config or {}).get("configurable", {}).get("user_id"))
    if err:
        return {"found": False, **err}

    try:
        order = ORDERS.get(order_id)
        refund = REFUNDS.get(order_id)
    except Exception:
        return {"found": False, **unexpected_error("request_refund")}

    if order is None or order["user_id"] != user_id:
        return {
            "found": False,
            "status": "not_found",
            "message": "Order not found.",
        }

    if refund is None:
        return {
            "found": False,
            "status": "not_found",
            "message": "Order not found.",
        }

    return {
        "found": True,
        "eligible": refund["eligible"],
        "status": refund["status"],
    }


@tool
def submit_refund(order_id: str, config: RunnableConfig) -> dict:
    """Submit a refund request for an eligible order.

    Idempotent: repeated calls for the same order return
    already_requested instead of creating a duplicate request.
    """

    order_id, err = validate_order_id(order_id)
    if err:
        return {"success": False, **err}

    user_id, err = validate_user_id((config or {}).get("configurable", {}).get("user_id"))
    if err:
        return {"success": False, **err}

    try:
        order = ORDERS.get(order_id)
        refund = REFUNDS.get(order_id)
    except Exception:
        return {"success": False, **unexpected_error("submit_refund")}

    if order is None or order["user_id"] != user_id:
        return {
            "success": False,
            "status": "not_found",
            "message": "Order not found.",
        }

    if refund is None:
        return {
            "success": False,
            "status": "not_found",
            "message": "Order not found.",
        }

    if not refund["eligible"]:
        return {
            "success": False,
            "status": "not_eligible",
            "message": "Order is not eligible for a refund.",
        }

    if refund["status"] == "already_refunded":
        return {
            "success": False,
            "status": "already_refunded",
            "message": "Refund has already been processed.",
        }

    if refund["status"] == "requested":
        return {
            "success": False,
            "status": "already_requested",
            "message": "Refund has already been requested.",
        }

    refund["status"] = "requested"

    return {
        "success": True,
        "status": "requested",
        "order_id": order_id,
    }
