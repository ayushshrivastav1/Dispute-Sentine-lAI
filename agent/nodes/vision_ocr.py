"""
DisputeSentinel AI — Multi-Modal Vision OCR Node (Node 2)

Analyzes Proof of Delivery (PoD) receipt images using a vision-language
model to detect recipient signatures, verify AWB codes, and confirm
recipient name matches. In development mode, returns deterministic
mock results based on delivery status.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from agent.graph.state import DisputeState

logger = logging.getLogger(__name__)

# Path to the vision prompt template
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "vision_pod.txt"


async def vision_ocr_node(state: DisputeState) -> dict:
    """Analyze Proof of Delivery image for signature and AWB verification.

    In development mode, returns mock results based on delivery status.
    In production, sends the PoD image to GPT-4o Vision for analysis.

    Args:
        state: Current DisputeState with extracted evidence.

    Returns:
        Dict with 'vision' and 'error_log' keys for state update.
    """
    errors: List[str] = []
    evidence = state.get("evidence")
    dispute_id = state.get("dispute_id", "unknown")

    # Default vision result for failure cases
    default_vision = {
        "pod_image_url": "",
        "signature_detected": False,
        "recipient_name_match": False,
        "ocr_extracted_awb": "",
        "confidence_score": 0.0,
    }

    if not evidence:
        errors.append("Vision: No evidence available — skipping OCR.")
        return {"vision": default_vision, "error_log": errors}

    pod_image_url = evidence.get("pod_image_url")
    if not pod_image_url:
        errors.append("Vision: No PoD image URL in evidence — skipping OCR.")
        return {"vision": default_vision, "error_log": errors}

    try:
        from agent.config import get_vision_llm
        from langchain_core.messages import HumanMessage

        has_groq = bool(os.environ.get("GROQ_API_KEY") and not os.environ.get("GROQ_API_KEY", "").startswith("your-"))
        has_openai = bool(os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENAI_API_KEY", "").startswith("your-"))

        if not (has_groq or has_openai):
            logger.warning("[SAFETY FALLBACK] No LLM keys configured for Vision OCR. Using heuristic parsing.")
            delivery_status = evidence.get("delivery_status", "UNKNOWN")
            customer_name = evidence.get("customer_name", "Unknown")
            awb_code = evidence.get("awb_code", "")
            return {
                "vision": {
                    "pod_image_url": pod_image_url,
                    "signature_detected": delivery_status == "DELIVERED",
                    "recipient_name_match": delivery_status == "DELIVERED",
                    "ocr_extracted_awb": awb_code if delivery_status == "DELIVERED" else "",
                    "confidence_score": 0.88 if delivery_status == "DELIVERED" else 0.15,
                },
                "error_log": ["Vision OCR ran in local heuristic mode (no LLM key provided)."]
            }

        # ── Production Mode: Call Vision LLM ──────────────
        from agent.config import get_vision_llm
        from langchain_core.messages import HumanMessage

        vision_llm = get_vision_llm()

        # Load and format the prompt template
        prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
        prompt_text = prompt_template.replace(
            "{expected_recipient}", evidence.get("customer_name", "")
        ).replace(
            "{expected_awb}", evidence.get("awb_code", "")
        )

        # Build the multi-modal message
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {"url": pod_image_url},
                },
            ]
        )

        response = await vision_llm.ainvoke([message])
        content = response.content

        # Parse JSON from the response (handle markdown code fences)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        parsed = json.loads(content)

        vision_result = {
            "pod_image_url": pod_image_url,
            "signature_detected": parsed.get("signature_detected", False),
            "recipient_name_match": parsed.get("recipient_name_match", False),
            "ocr_extracted_awb": parsed.get("ocr_extracted_awb", ""),
            "confidence_score": float(parsed.get("confidence_score", 0.0)),
        }

        logger.info(
            "Vision OCR for %s: sig=%s, name_match=%s, confidence=%.2f",
            dispute_id,
            vision_result["signature_detected"],
            vision_result["recipient_name_match"],
            vision_result["confidence_score"],
        )

        return {"vision": vision_result, "error_log": errors}

    except Exception as e:
        logger.error("Vision OCR failed for %s: %s", dispute_id, str(e))
        errors.append(f"Vision Error: {str(e)}")
        return {"vision": default_vision, "error_log": errors}
