"""
DisputeSentinel AI — Escalation Node (Node 4B)

Handles cases that cannot be auto-contested:
  - ESCALATE_HUMAN: Persists draft dossier, marks as AWAITING_REVIEW,
    and would emit a websocket notification to the Analyst Terminal.
  - AUTO_ACCEPT: Submits an accept call to Razorpay, conceding the
    chargeback when win probability is below viability cutoff.
"""

import os
import logging
from typing import Dict, Any, List

from agent.graph.state import DisputeState
from agent.tools.razorpay_sdk import RazorpayClient

logger = logging.getLogger(__name__)


async def escalation_node(state: DisputeState) -> dict:
    """Route dispute to human review or auto-accept based on decision.

    Args:
        state: Current DisputeState with evidence and decision route.

    Returns:
        Dict with submission_status, formatted_dossier, and error_log.
    """
    errors: List[str] = []
    decision_route = state.get("decision_route", "ESCALATE_HUMAN")
    dispute_id = state.get("dispute_id", "unknown")
    dispute_amount = state.get("dispute_amount", 0)
    p_win = state.get("calculated_win_probability", 0.0)
    evidence = state.get("evidence") or {}
    vision = state.get("vision") or {}

    try:
        if decision_route == "ESCALATE_HUMAN":
            # ── Human Review Escalation ───────────────────
            # Compile a draft dossier for the analyst to review/edit
            draft_dossier: Dict[str, Any] = {
                "action": "draft",
                "amount": dispute_amount,
                "summary": (
                    f"Dispute {dispute_id} escalated for human review. "
                    f"Win probability: {p_win:.3f}. "
                    f"Delivery status: {evidence.get('delivery_status', 'UNKNOWN')}. "
                    f"Signature detected: {vision.get('signature_detected', False)}."
                ),
                "evidence_snapshot": {
                    "delivery_status": evidence.get("delivery_status"),
                    "carrier": evidence.get("carrier_name"),
                    "awb": evidence.get("awb_code"),
                    "signature_verified": vision.get("signature_detected"),
                    "confidence": vision.get("confidence_score"),
                    "customer_orders": evidence.get("successful_orders"),
                    "prior_disputes": evidence.get("prior_disputes"),
                },
                "escalation_reasons": [],
            }

            # Document why this was escalated
            if dispute_amount >= 2_500_000:
                draft_dossier["escalation_reasons"].append(
                    f"Amount ₹{dispute_amount / 100:,.0f} exceeds auto-contest limit (₹25,000)"
                )
            if 0.40 <= p_win < 0.75:
                draft_dossier["escalation_reasons"].append(
                    f"Win probability {p_win:.3f} is in the uncertain range (0.40–0.75)"
                )

            logger.info(
                "Escalated dispute %s to human review: P_win=%.3f, Amount=₹%.0f, Reasons=%s",
                dispute_id,
                p_win,
                dispute_amount / 100,
                draft_dossier["escalation_reasons"],
            )

            return {
                "formatted_dossier": draft_dossier,
                "submission_status": "AWAITING_REVIEW",
                "error_log": errors,
            }

        elif decision_route == "AUTO_ACCEPT":
            # ── Auto-Accept: Concede the chargeback ───────
            logger.info(
                "Auto-accepting dispute %s: P_win=%.3f is below viability cutoff",
                dispute_id,
                p_win,
            )

            client = RazorpayClient()
            response = await client.accept_dispute(dispute_id)

            accept_dossier: Dict[str, Any] = {
                "action": "accept",
                "dispute_id": dispute_id,
                "reason": f"Win probability {p_win:.3f} below viability threshold (0.40)",
                "api_response": response,
            }

            logger.info(
                "Dispute %s auto-accepted: status=%s",
                dispute_id,
                response.get("status", "unknown"),
            )

            return {
                "formatted_dossier": accept_dossier,
                "submission_status": "ACCEPTED",
                "error_log": errors,
            }

        else:
            # Unexpected route — safe fallback to escalation
            errors.append(f"Unexpected decision_route: {decision_route}")
            return {
                "submission_status": "AWAITING_REVIEW",
                "error_log": errors,
            }

    except Exception as e:
        logger.error("Escalation failed for %s: %s", dispute_id, str(e))
        errors.append(f"Escalation Error: {str(e)}")
        return {
            "submission_status": "FAILED",
            "error_log": errors,
        }
