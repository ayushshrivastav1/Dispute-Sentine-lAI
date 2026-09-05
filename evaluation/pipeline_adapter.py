"""
DisputeSentinel AI — Pipeline Evaluation Adapter
Executes the full multi-agent dispute processing chain for a test case:
Evidence Extraction -> Multi-Modal Vision -> Policy Gate -> Audit Record
"""

import os
from typing import Dict, Any
from agent.nodes.policy_gate import policy_gate_node, POLICY_VERSION
from agent.nodes.generator import _build_evidence_summary

def evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the end-to-end evaluation pipeline against a held-out dispute case.
    """
    amount = int(float(case.get("dispute_amount", 0)))
    dispute_id = str(case.get("dispute_id", "disp_eval"))
    reason = str(case.get("reason_code", "unknown"))

    # 1. Structure Evidence
    evidence = {
        "delivery_status": str(case.get("delivery_status", "UNKNOWN")).upper(),
        "carrier_name": str(case.get("carrier", "delhivery")),
        "awb_code": f"AWB_{dispute_id[-6:]}",
        "shipping_address": "Customer Address Verified" if case.get("ip_billing_match") in [True, "True", "true", 1, "1"] else "Remote Address",
        "billing_address": "Customer Address Verified",
        "ip_address": "103.21.58.77",
        "known_ip_addresses": ["103.21.58.77"] if case.get("ip_billing_match") in [True, "True", "true", 1, "1"] else [],
        "successful_orders": int(case.get("device_reuse_count", 0) or 0),
        "prior_disputes": 0,
        "days_to_filing": int(case.get("days_to_filing", 0) or 0),
        "delivery_timestamp": "2026-08-28T14:45:00Z" if case.get("delivery_status") == "DELIVERED" else None
    }

    # 2. Vision OCR Layer
    pod_sig = case.get("pod_signature_detected") in [True, "True", "true", 1, "1"]
    pod_match = case.get("pod_name_match") in [True, "True", "true", 1, "1"]
    ocr_conf = float(case.get("ocr_confidence", 0.0) or 0.0)

    vision = {
        "pod_image_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/George_Washington_signature.svg" if pod_sig else None,
        "signature_detected": pod_sig,
        "recipient_name_match": pod_match,
        "ocr_extracted_awb": evidence["awb_code"] if pod_sig else "",
        "confidence_score": ocr_conf
    }

    # 3. Policy Gate Evaluation
    state = {
        "dispute_id": dispute_id,
        "dispute_amount": amount,
        "dispute_reason": reason,
        "evidence": evidence,
        "vision": vision
    }

    policy_result = policy_gate_node(state)
    decision = policy_result.get("decision_route", "HUMAN_REVIEW")
    win_prob = policy_result.get("calculated_win_probability", 0.0)

    # 4. Generate LLM evidence summary validation
    evidence_summary = _build_evidence_summary(evidence, vision, amount)

    # 5. Build Comprehensive Audit Record
    audit_record = {
        "dispute_id": dispute_id,
        "decision": decision,
        "policy_score": round(win_prob, 3),
        "threshold": 0.75,
        "amount_inr": amount / 100 if amount > 10000 else amount,
        "evidence": [
            k for k, v in [
                ("delivery_verified", evidence["delivery_status"] == "DELIVERED"),
                ("signature_verified", vision["signature_detected"]),
                ("recipient_match", vision["recipient_name_match"]),
                ("ip_verified", bool(evidence["known_ip_addresses"]))
            ] if v
        ],
        "model": "groq/llama-3.3-70b-versatile",
        "policy_version": POLICY_VERSION,
        "action": "razorpay_contest" if decision == "AUTO_CONTEST" else "escalate_to_human",
        "success": decision == "AUTO_CONTEST"
    }

    # Binary prediction for evaluation: 1 = should contest / won, 0 = do not contest / lost
    predicted_binary = 1 if decision in ["AUTO_CONTEST", "HUMAN_REVIEW"] and win_prob >= 0.60 else 0

    return {
        "dispute_id": dispute_id,
        "predicted": predicted_binary,
        "decision": decision,
        "policy_score": win_prob,
        "audit_record": audit_record,
        "evidence_summary": evidence_summary
    }
