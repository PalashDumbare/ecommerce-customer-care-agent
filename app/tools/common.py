"""Shared validation and error helpers for the business tools.

These live in the tool/business layer because validation and safety must
be enforced at the point of data access, never left to the LLM.
"""
import logging
import re

logger = logging.getLogger(__name__)

ORDER_ID_PATTERN = re.compile(r"^ORD\d+$")


def validate_order_id(order_id):
    """Validate and normalize an order ID.

    Returns (order_id, error_result). error_result is None when valid.
    """
    if order_id is None or str(order_id).strip() == "":
        return None, {
            "status": "invalid_order_id",
            "message": "A valid order ID is required.",
        }
    order_id = str(order_id).strip().upper()
    if not ORDER_ID_PATTERN.fullmatch(order_id):
        return None, {
            "status": "invalid_order_id",
            "message": "Invalid order ID format. Expected something like ORD1001.",
        }
    return order_id, None


def validate_user_id(user_id):
    """Validate the authenticated user read from the trusted config channel."""
    if user_id is None or str(user_id).strip() == "":
        return None, {
            "status": "invalid_user_id",
            "message": "Your session is not authenticated.",
        }
    return str(user_id).strip(), None


def unexpected_error(operation):
    """Log an unexpected failure and return a safe structured result.

    Never lets a raw exception reach the user, but always records it
    so nothing is silently swallowed.
    """
    logger.error("Unexpected failure during %s", operation, exc_info=True)
    return {
        "status": "error",
        "message": "Something went wrong processing your request.",
    }
