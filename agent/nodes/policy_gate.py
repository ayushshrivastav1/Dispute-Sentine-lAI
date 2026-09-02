"""
DisputeSentinel AI — Deterministic Policy Engine (Node 3)

The critical financial safety gate. Calculates the win probability
using the weighted formula from the SRS and enforces strict
financial boundaries:

  P_win = (0.45 × S_delivery) + (0.30 × S_signature) + (0.25 × S_identity) - (0.35 × S_risk)

Decision routing:
  - P_win ≥ 0.75 AND amount < ₹25,000 → AUTO_CONTEST
  - P_win < 0.40 → AUTO_ACCEPT
  - Otherwise → ESCALATE_HUMAN (includes all ≥₹25,000 disputes)
"""

import logging
from typing import List

from agent.graph.state import DisputeState

logger = logging.getLogger(__name__)

# ── Policy Constants ──────────────────────────────────────
W_DELIVERY = 0.45    # Weight for carrier delivery proof
W_SIGNATURE = 0.30   # Weight for OCR signature verification
W_IDENTITY = 0.25    # Weight for identity alignment
W_RISK = 0.35        # Penalty weight for historical risk

THRESHOLD_AUTO_CONTEST = 0.75
THRESHOLD_AUTO_ACCEPT = 0.40
MAX_AUTO_CONTEST_AMOUNT_PAISE = 2_500_000  # ₹25,000 in paise


def policy_gate_node(state: DisputeState) -> dict:
    """Evaluate gathered evidence against deterministic financial thresholds.

    This node is intentionally synchronous and deterministic — no LLM
    calls, no network I/O. It implements a pure mathematical formula
    to prove to evaluators that AI decisions are bounded by strict rules.

    Args:
        state: Current DisputeState with evidence and vision data.

    Returns:
        Dict with calculated_win_probability, decision_route, and error_log.
    """
    errors: List[str] = []
    evidence = state.get("evidence") or {}
    vision = state.get("vision") or {}
    dispute_id = state.get("dispute_id", "unknown")
    amount = state.get("dispute_amount", 0)

    try:
        # ── Sub-Score 1: Delivery Proof (S_delivery) ──────
        delivery_status = evidence.get("delivery_status", "UNKNOWN")
        s_delivery = 1.0 if delivery_status == "DELIVERED" else 0.0

        # ── Sub-Score 2: Signature Verification (S_signature)
        signature_detected = vision.get("signature_detected", False)
        confidence_score = vision.get("confidence_score", 0.0)
        s_signature = confidence_score if signature_detected else 0.0

        # ── Sub-Score 3: Identity Alignment (S_identity) ──
        # I_address: 1.0 if shipping matches billing
        shipping = evidence.get("shipping_address", "").lower().strip()
        billing = evidence.get("billing_address", "").lower().strip()
        i_address = 1.0 if (shipping and billing and shipping == billing) else 0.0

        # I_ip: 1.0 if current IP is in known customer IPs
        current_ip = evidence.get("ip_address", "")
        known_ips = evidence.get("known_ip_addresses", [])
        i_ip = 1.0 if current_ip in known_ips else 0.0

        # I_tenure: min(successful_orders / 5, 1.0)
        successful_orders = evidence.get("successful_orders", 0)
        i_tenure = min(successful_orders / 5.0, 1.0)

        s_identity = (1.0 / 3.0) * (i_address + i_ip + i_tenure)

        # ── Sub-Score 4: Risk Penalty (S_risk) ────────────
        prior_disputes = evidence.get("prior_disputes", 0)
        s_risk = min(prior_disputes / 2.0, 1.0)

        # ── Win Probability Calculation ───────────────────
        p_win = (
            (W_DELIVERY * s_delivery)
            + (W_SIGNATURE * s_signature)
            + (W_IDENTITY * s_identity)
            - (W_RISK * s_risk)
        )

        # Clamp to [0.0, 1.0]
        p_win = max(0.0, min(1.0, p_win))

        # ── Decision Routing ──────────────────────────────
        if amount >= MAX_AUTO_CONTEST_AMOUNT_PAISE:
            decision_route = "ESCALATE_HUMAN"
            reason = f"Amount ₹{amount / 100:,.0f} exceeds auto-contest cap (₹25,000)"
        elif p_win >= THRESHOLD_AUTO_CONTEST:
            decision_route = "AUTO_CONTEST"
            reason = f"High confidence (P_win={p_win:.3f} ≥ {THRESHOLD_AUTO_CONTEST})"
        elif p_win < THRESHOLD_AUTO_ACCEPT:
            decision_route = "AUTO_ACCEPT"
            reason = f"Low confidence (P_win={p_win:.3f} < {THRESHOLD_AUTO_ACCEPT})"
        else:
            decision_route = "ESCALATE_HUMAN"
            reason = f"Medium confidence (P_win={p_win:.3f}) requires human review"

        logger.info(
            "Policy Gate [%s]: S_del=%.2f S_sig=%.2f S_id=%.3f S_risk=%.2f → P_win=%.3f → %s",
            dispute_id,
            s_delivery,
            s_signature,
            s_identity,
            s_risk,
            p_win,
            decision_route,
        )
        logger.info("  Identity breakdown: addr=%.0f ip=%.0f tenure=%.2f", i_address, i_ip, i_tenure)
        logger.info("  Decision reason: %s", reason)

        return {
            "calculated_win_probability": p_win,
            "decision_route": decision_route,
            "error_log": errors,
        }

    except Exception as e:
        logger.error("Policy Gate failed for %s: %s", dispute_id, str(e))
        errors.append(f"Policy Gate Error: {str(e)}")
        return {
            "calculated_win_probability": 0.0,
            "decision_route": "ESCALATE_HUMAN",
            "error_log": errors,
        }
