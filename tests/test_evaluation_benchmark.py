"""
DisputeSentinel AI — Automated Risk Evaluation Benchmark Test
Validates that the full multi-agent pipeline achieves >= 90% Precision,
>= 85% Recall, <= 10% FPR, and positive ROI on the strictly held-out test dataset.
"""

import pytest
from evaluation.evaluate import run_held_out_evaluation

def test_risk_manager_evaluation_bar():
    report = run_held_out_evaluation()
    metrics = report["metrics"]
    financials = report["financial_impact"]

    # 1. Dataset adequacy: Benchmark must contain at least 50 held-out cases
    assert report["dataset_size"] >= 50, (
        f"Held-out dataset size {report['dataset_size']} is insufficient (minimum 50 required)"
    )

    # 2. Precision Bar: >= 90% of auto-contested cases must be true wins (avoids merchant fee loss)
    assert metrics["precision_pct"] >= 90.0, (
        f"Precision {metrics['precision_pct']}% fell below the 90.0% Risk Manager threshold"
    )

    # 3. Recall Bar: >= 85% of legitimate winnable disputes must be captured
    assert metrics["recall_pct"] >= 85.0, (
        f"Recall {metrics['recall_pct']}% fell below the 85.0% Risk Manager threshold"
    )

    # 4. False Positive Rate: <= 10.0%
    assert metrics["false_positive_rate_pct"] <= 10.0, (
        f"False positive rate {metrics['false_positive_rate_pct']}% exceeded 10.0% threshold"
    )

    # 5. Financial ROI: Net saved capital must be positive and ROI multiplier >= 10x
    assert financials["net_value_saved_inr"] > 0, "Net value saved must be positive"
    assert financials["roi_multiplier"] >= 10.0, (
        f"Financial ROI multiplier {financials['roi_multiplier']}x fell below 10.0x threshold"
    )
