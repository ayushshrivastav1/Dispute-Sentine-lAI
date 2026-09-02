"""
DisputeSentinel AI — Evidence Extractor Node (Node 1)

Ingests order data, customer purchase history, device fingerprint,
and carrier delivery telemetry. Produces a flat ExtractedEvidence
dict conforming to the graph state schema.
"""

import logging
from typing import Dict, Any, List

from agent.graph.state import DisputeState
from agent.tools.db_client import fetch_order_details, fetch_customer_history
from agent.tools.carrier_api import track_shipment

logger = logging.getLogger(__name__)


async def evidence_extractor_node(state: DisputeState) -> dict:
    """Extract and normalize all available evidence for a dispute.

    Reads dispute_id and payment_id from state, queries the order
    database, customer history, and carrier tracking API, then
    produces a flat ExtractedEvidence dictionary.

    Args:
        state: Current DisputeState with dispute identifiers.

    Returns:
        Dict with 'evidence' and 'error_log' keys for state update.
    """
    errors: List[str] = []
    dispute_id = state.get("dispute_id", "unknown")
    payment_id = state.get("payment_id", "")

    logger.info("Extracting evidence for dispute %s (payment %s)", dispute_id, payment_id)

    if not payment_id:
        errors.append("Extractor: No payment_id available in state.")
        return {"evidence": None, "error_log": errors}

    try:
        # ── Step 1: Fetch order details ───────────────────
        order = await fetch_order_details(payment_id)
        logger.info("Fetched order %s for payment %s", order.get("order_id"), payment_id)

        # ── Step 2: Fetch customer history ────────────────
        customer_email = order.get("customer_email", "")
        history = await fetch_customer_history(customer_email)
        logger.info(
            "Customer %s: %d orders, %d disputes",
            customer_email,
            history.get("successful_orders", 0),
            history.get("previous_disputes", 0),
        )

        # ── Step 3: Fetch carrier tracking ────────────────
        awb_code = order.get("awb_code", "")
        carrier_name = order.get("carrier_name", "")
        tracking: Dict[str, Any] = {}

        if awb_code and carrier_name:
            try:
                tracking = await track_shipment(awb_code, carrier_name)
                logger.info("Tracking %s: status=%s", awb_code, tracking.get("status"))
            except Exception as track_err:
                errors.append(f"Carrier tracking failed for {awb_code}: {str(track_err)}")
                logger.warning("Carrier tracking failed: %s", track_err)
        else:
            errors.append("Extractor: Missing AWB or carrier info in order.")

        # ── Step 4: Assemble flat ExtractedEvidence ───────
        evidence = {
            "order_id": order.get("order_id", ""),
            "amount": order.get("amount", 0),
            "currency": order.get("currency", "INR"),
            "customer_name": order.get("customer_name", ""),
            "customer_email": customer_email,
            "shipping_address": order.get("shipping_address", ""),
            "billing_address": order.get("billing_address", ""),
            "carrier_name": carrier_name,
            "awb_code": awb_code,
            "delivery_status": tracking.get("status", "UNKNOWN"),
            "delivery_timestamp": tracking.get("delivery_timestamp"),
            "delivery_gps": tracking.get("delivery_gps"),
            "ip_address": order.get("ip_address", "0.0.0.0"),
            "device_fingerprint": order.get("device_fingerprint", "unknown"),
            "successful_orders": history.get("successful_orders", 0),
            "prior_disputes": history.get("previous_disputes", 0),
            "account_tenure_days": history.get("account_tenure_days", 0),
            "known_ip_addresses": history.get("ip_addresses", []),
            "pod_image_url": tracking.get("pod_image_url"),
        }

        logger.info(
            "Evidence assembled for dispute %s: delivery=%s, orders=%d, disputes=%d",
            dispute_id,
            evidence["delivery_status"],
            evidence["successful_orders"],
            evidence["prior_disputes"],
        )

        return {"evidence": evidence, "error_log": errors}

    except Exception as e:
        logger.error("Evidence extraction failed for %s: %s", dispute_id, str(e))
        errors.append(f"Extractor Error: {str(e)}")
        return {"evidence": None, "error_log": errors}
