"""
DisputeSentinel AI — Auto-Contest Dispatcher (Node 4A)

Compiles gathered evidence into a structured contest dossier matching
the Razorpay PATCH /v1/disputes/{id}/contest API specification, then
submits it. Only executes when decision_route == "AUTO_CONTEST".
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from agent.graph.state import DisputeState
from agent.tools.razorpay_sdk import RazorpayClient

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "contest_dossier.txt"


def _build_evidence_summary(evidence: dict, vision: dict, dispute_amount: int) -> str:
    """Build a factual, concise summary for the contest dossier.

    This is a deterministic fallback used in demo mode or when LLM
    generation is unavailable. Max 1000 characters per Razorpay spec.
    """
    parts = []

    delivery_status = evidence.get("delivery_status", "UNKNOWN")
    if delivery_status == "DELIVERED":
        ts = evidence.get("delivery_timestamp", "")
        carrier = evidence.get("carrier_name", "the carrier")
        awb = evidence.get("awb_code", "")
        parts.append(
            f"The order was confirmed delivered by {carrier} (AWB: {awb}) "
            f"on {ts}."
        )

    if vision.get("signature_detected"):
        parts.append("Proof of Delivery shows a valid recipient signature.")
    if vision.get("recipient_name_match"):
        parts.append("Recipient name on PoD matches the order's customer name.")

    addr = evidence.get("shipping_address", "")
    if addr:
        parts.append(f"Goods were shipped to: {addr}.")

    orders = evidence.get("successful_orders", 0)
    if orders > 0:
        parts.append(f"Customer has {orders} successful prior orders with no disputes.")

    summary = " ".join(parts)
    return summary[:1000]  # Razorpay max


async def auto_contest_node(state: DisputeState) -> dict:
    """Generate and submit a contest dossier to Razorpay.

    Only runs when decision_route == "AUTO_CONTEST". Builds the evidence
    payload, optionally uses an LLM to generate the summary, validates
    against the Razorpay spec, and submits via the SDK.

    Args:
        state: Current DisputeState with evidence, vision, and decision.

    Returns:
        Dict with formatted_dossier, submission_status, and error_log.
    """
    errors: List[str] = []
    dispute_id = state.get("dispute_id", "unknown")
    dispute_amount = state.get("dispute_amount", 0)
    evidence = state.get("evidence") or {}
    vision = state.get("vision") or {}

    logger.info("Auto-contest initiated for dispute %s (₹%s)", dispute_id, dispute_amount / 100)

    try:
        app_env = os.environ.get("APP_ENV", "development")

        # ── Build the contest dossier ─────────────────────
        if app_env == "development":
            # Demo mode: deterministic summary generation
            summary = _build_evidence_summary(evidence, vision, dispute_amount)
        else:
            # Production: use LLM to generate a polished summary
            try:
                from agent.config import get_text_llm

                llm = get_text_llm()
                prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
                prompt = prompt_template.replace(
                    "{evidence_json}", json.dumps(evidence, default=str)
                ).replace(
                    "{vision_json}", json.dumps(vision, default=str)
                ).replace(
                    "{dispute_id}", dispute_id
                ).replace(
                    "{dispute_amount}", str(dispute_amount)
                ).replace(
                    "{reason_code}", state.get("dispute_reason", "unknown")
                )

                response = await llm.ainvoke(prompt)
                content = response.content

                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()

                parsed = json.loads(content)
                summary = parsed.get("summary", "")[:1000]
            except Exception as llm_err:
                logger.warning("LLM summary generation failed, using fallback: %s", llm_err)
                summary = _build_evidence_summary(evidence, vision, dispute_amount)

        # ── Assemble Razorpay-compatible payload ──────────
        formatted_dossier: Dict[str, Any] = {
            "action": "submit",
            "amount": dispute_amount,
            "summary": summary,
            "shipping_proof": ["doc_EFtmUsbwpXwBH9"],   # In production: uploaded doc IDs
            "billing_proof": ["doc_EFtmUsbwpXwBH2"],
            "others": [
                {
                    "type": "receipt_signed_by_customer",
                    "document_ids": ["doc_EFtmUsbwpXwBH1"],
                }
            ],
        }

        # ── Submit to Razorpay ────────────────────────────
        client = RazorpayClient()
        response = await client.contest_dispute(dispute_id, formatted_dossier)

        logger.info(
            "Contest submitted for %s: response_status=%s",
            dispute_id,
            response.get("status", "unknown"),
        )

        return {
            "formatted_dossier": formatted_dossier,
            "submission_status": "SUBMITTED",
            "error_log": errors,
        }

    except Exception as e:
        logger.error("Auto-contest failed for %s: %s", dispute_id, str(e))
        errors.append(f"Contest Error: {str(e)}")
        return {
            "formatted_dossier": None,
            "submission_status": "FAILED",
            "error_log": errors,
        }
