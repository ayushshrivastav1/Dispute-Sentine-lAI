"""
DisputeSentinel AI — LangGraph Compiled Execution Runtime

Builds, compiles, and executes the multi-node dispute resolution
state machine. This is the central orchestrator that wires together
all agent nodes with conditional routing and checkpointed execution.

Pipeline:
  [START] → evidence_extractor → vision_ocr → policy_gate
                                                   │
                                    ┌──────────────┼──────────────┐
                                    ▼              ▼              ▼
                              auto_contest   escalation     escalation
                              (AUTO_CONTEST) (ESCALATE)     (AUTO_ACCEPT)
                                    │              │              │
                                    └──────────────┴──────────────┘
                                                   │
                                                 [END]
"""

import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agent.graph.state import DisputeState
from agent.nodes.extractor import evidence_extractor_node
from agent.nodes.vision_ocr import vision_ocr_node
from agent.nodes.policy_gate import policy_gate_node
from agent.nodes.generator import auto_contest_node
from agent.nodes.escalation import escalation_node

logger = logging.getLogger(__name__)


def _route_after_policy(
    state: DisputeState,
) -> Literal["auto_contest", "escalation"]:
    """Conditional router after the policy gate node.

    Routes to auto_contest if decision is AUTO_CONTEST,
    otherwise routes to escalation (covers both ESCALATE_HUMAN
    and AUTO_ACCEPT, which the escalation node handles internally).
    """
    route = state.get("decision_route", "ESCALATE_HUMAN")

    if route == "AUTO_CONTEST":
        logger.info(
            "Routing to AUTO_CONTEST for dispute %s (P_win=%.3f)",
            state.get("dispute_id", "unknown"),
            state.get("calculated_win_probability", 0.0),
        )
        return "auto_contest"
    else:
        logger.info(
            "Routing to ESCALATION for dispute %s (route=%s, P_win=%.3f)",
            state.get("dispute_id", "unknown"),
            route,
            state.get("calculated_win_probability", 0.0),
        )
        return "escalation"


def build_dispute_graph() -> StateGraph:
    """Construct the LangGraph state machine for dispute resolution.

    Returns:
        Compiled StateGraph ready for execution with checkpointing.
    """
    workflow = StateGraph(DisputeState)

    # ── Register Nodes ────────────────────────────────────
    workflow.add_node("evidence_extractor", evidence_extractor_node)
    workflow.add_node("vision_ocr", vision_ocr_node)
    workflow.add_node("policy_gate", policy_gate_node)
    workflow.add_node("auto_contest", auto_contest_node)
    workflow.add_node("escalation", escalation_node)

    # ── Wire Sequential Edges ─────────────────────────────
    workflow.add_edge(START, "evidence_extractor")
    workflow.add_edge("evidence_extractor", "vision_ocr")
    workflow.add_edge("vision_ocr", "policy_gate")

    # ── Conditional Branching After Policy Gate ───────────
    workflow.add_conditional_edges(
        "policy_gate",
        _route_after_policy,
        {
            "auto_contest": "auto_contest",
            "escalation": "escalation",
        },
    )

    # ── Terminal Edges ────────────────────────────────────
    workflow.add_edge("auto_contest", END)
    workflow.add_edge("escalation", END)

    return workflow


def compile_graph(checkpointer: MemorySaver | None = None) -> StateGraph:
    """Build and compile the dispute resolution graph.

    Args:
        checkpointer: Optional MemorySaver for state persistence across
                      invocations. If None, a new MemorySaver is created.

    Returns:
        Compiled graph ready for .invoke() or .ainvoke() calls.
    """
    if checkpointer is None:
        checkpointer = MemorySaver()

    workflow = build_dispute_graph()
    compiled = workflow.compile(checkpointer=checkpointer)

    logger.info("DisputeSentinel graph compiled successfully with checkpointing.")
    return compiled


async def run_dispute_pipeline(
    dispute_id: str,
    webhook_payload: dict,
    thread_id: str | None = None,
) -> DisputeState:
    """Execute the full dispute resolution pipeline.

    This is the primary entry point called by the webhook handler
    after HMAC verification succeeds.

    Args:
        dispute_id: Razorpay dispute identifier (disp_...).
        webhook_payload: Raw parsed webhook event payload.
        thread_id: Optional thread ID for checkpointed execution.
                   Defaults to dispute_id for idempotency.

    Returns:
        Final DisputeState after all nodes have executed.
    """
    if thread_id is None:
        thread_id = dispute_id

    logger.info("Starting dispute pipeline for %s", dispute_id)

    # Extract dispute details from webhook payload
    dispute_entity = webhook_payload.get("payload", {}).get("dispute", {}).get("entity", {})
    payment_entity = webhook_payload.get("payload", {}).get("payment", {}).get("entity", {})

    # Initialize state from webhook data
    initial_state: DisputeState = {
        "dispute_id": dispute_id,
        "payment_id": payment_entity.get("id", ""),
        "dispute_reason": dispute_entity.get("reason_code", "unknown"),
        "dispute_amount": dispute_entity.get("amount", 0),
        "due_by": dispute_entity.get("respond_by", 0),
        "raw_webhook_payload": webhook_payload,
        "evidence": None,
        "vision": None,
        "calculated_win_probability": 0.0,
        "decision_route": "PENDING",
        "formatted_dossier": None,
        "submission_status": "PENDING",
        "error_log": [],
        "audit_hash": None,
    }

    # Compile and execute
    graph = compile_graph()
    config = {"configurable": {"thread_id": thread_id}}

    try:
        final_state = await graph.ainvoke(initial_state, config=config)
        logger.info(
            "Pipeline completed for %s: route=%s, status=%s, P_win=%.3f",
            dispute_id,
            final_state.get("decision_route"),
            final_state.get("submission_status"),
            final_state.get("calculated_win_probability", 0.0),
        )
        return final_state

    except Exception as e:
        logger.error("Pipeline execution failed for %s: %s", dispute_id, str(e))
        initial_state["error_log"] = [f"Pipeline execution failed: {str(e)}"]
        initial_state["submission_status"] = "FAILED"
        return initial_state
