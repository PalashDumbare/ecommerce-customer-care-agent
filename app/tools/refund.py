from langchain_core.tools import tool

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
}


@tool(
    description= """
        Request a refund for an order, or check the status
        of a refund for a user.
    as
        Use this when the customer asks for a refund or
        asks about the status of an existing refund.
        """
)
def request_refund(order_id: str, user_id: str):

    refund = REFUNDS.get(order_id)

    if not refund:
        return {
            "found": False,
            "message": "Order not found."
        }

    if refund["status"] == "already_refunded":
        return {
            "found": True,
            "eligible": False,
            "status": "already_refunded"
        }

    return {
        "found": True,
        "eligible": refund["eligible"],
        "status": refund["status"],
    }


@tool
def submit_refund(order_id: str, user_id: str):
    """Submit a refund request for an eligible order."""

    refund = REFUNDS.get(order_id)

    if not refund:
        return {
            "success": False,
            "message": "Order not found."
        }

    if not refund["eligible"]:
        return {
            "success": False,
            "message": "Order is not eligible for a refund."
        }

    if refund["status"] == "already_refunded":
        return {
            "success": False,
            "message": "Refund has already been processed."
        }

    refund["status"] = "requested"

    return {
        "success": True,
        "order_id": order_id,
        "status": "requested"
    }
