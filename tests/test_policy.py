"""
DisputeSentinel AI — Tests for Policy Gate Logic
"""

from agent.nodes.policy_gate import policy_gate_node

def test_policy_gate_auto_contest_high_confidence():
    """Test policy routes to AUTO_CONTEST when P_win >= 0.75 and amount < ₹25,000."""
    state = {
        "dispute_id": "disp_test1",
        "dispute_amount": 1000000,  # ₹10,000
        "evidence": {
            "delivery_status": "DELIVERED",
            "shipping_address": "same_address",
            "billing_address": "same_address",
            "ip_address": "1.1.1.1",
            "known_ip_addresses": ["1.1.1.1"],
            "successful_orders": 10,
            "prior_disputes": 0,
        },
        "vision": {
            "signature_detected": True,
            "confidence_score": 0.95
        }
    }
    
    # Expected: S_del=1.0, S_sig=0.95, S_id=1.0, S_risk=0
    # P_win = (0.45*1.0) + (0.30*0.95) + (0.25*1.0) - 0 = 0.45 + 0.285 + 0.25 = 0.985
    
    result = policy_gate_node(state)
    assert result["decision_route"] == "AUTO_CONTEST"
    assert result["calculated_win_probability"] > 0.75

def test_policy_gate_escalate_large_amount():
    """Test policy routes to ESCALATE_HUMAN regardless of P_win if amount >= ₹25,000."""
    state = {
        "dispute_id": "disp_test2",
        "dispute_amount": 3500000,  # ₹35,000 (Above limit)
        "evidence": {
            "delivery_status": "DELIVERED",
            "shipping_address": "same",
            "billing_address": "same",
            "ip_address": "1.1.1.1",
            "known_ip_addresses": ["1.1.1.1"],
            "successful_orders": 10,
            "prior_disputes": 0,
        },
        "vision": {
            "signature_detected": True,
            "confidence_score": 0.95
        }
    }
    
    result = policy_gate_node(state)
    assert result["decision_route"] == "ESCALATE_HUMAN"

def test_policy_gate_low_confidence_escalation_guardrail():
    """Test policy safely routes low confidence (P_win < 0.40) to ESCALATE_HUMAN.
    
    Safety invariant: On Razorpay, dispute acceptance is irreversible and forfeiture
    of merchant funds must never occur automatically without human confirmation.
    """
    state = {
        "dispute_id": "disp_test3",
        "dispute_amount": 500000,  # ₹5,000
        "evidence": {
            "delivery_status": "UNKNOWN",
            "shipping_address": "diff1",
            "billing_address": "diff2",
            "ip_address": "2.2.2.2",
            "known_ip_addresses": ["1.1.1.1"],
            "successful_orders": 0,
            "prior_disputes": 2,  # Max penalty
        },
        "vision": {
            "signature_detected": False,
            "confidence_score": 0.0
        }
    }
    
    # Expected: S_del=0, S_sig=0, S_id=0, S_risk=1.0
    # P_win = 0 + 0 + 0 - 0.35 = 0 (clamped to 0)
    
    result = policy_gate_node(state)
    assert result["decision_route"] == "ESCALATE_HUMAN"
    assert result["calculated_win_probability"] < 0.40

def test_policy_gate_escalate_uncertain():
    """Test policy routes to ESCALATE_HUMAN when P_win is between 0.40 and 0.75."""
    state = {
        "dispute_id": "disp_test4",
        "dispute_amount": 500000,  # ₹5,000
        "evidence": {
            "delivery_status": "DELIVERED", # S_del=1.0 * 0.45 = 0.45
            "shipping_address": "diff1",
            "billing_address": "diff2",
            "ip_address": "1.1.1.1",
            "known_ip_addresses": ["1.1.1.1"],
            "successful_orders": 1, 
            "prior_disputes": 0,
        },
        "vision": {
            "signature_detected": False, # S_sig=0
            "confidence_score": 0.0
        }
    }
    
    result = policy_gate_node(state)
    assert result["decision_route"] == "ESCALATE_HUMAN"
    assert 0.40 <= result["calculated_win_probability"] < 0.75
