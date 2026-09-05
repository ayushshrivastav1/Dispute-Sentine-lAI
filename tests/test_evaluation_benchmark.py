"""
DisputeSentinel AI — Automated Risk Evaluation Benchmark Test
Validates that the policy and scoring model achieves >= 90% Precision,
>= 85% Recall, and >= 3x ROI on the held-out test dataset.
"""

import pytest
from evaluation.evaluate import run_evaluation

def test_risk_manager_evaluation_bar():
    report = run_evaluation()
    metrics = report["metrics"]
    financials = report["financial_impact_inr"]

    # 1. Precision Bar: >= 90% of auto-contested cases must be true wins (avoids merchant fee loss)
    assert metrics["precision_pct"] >= 90.0, (
        f"Precision {metrics['precision_pct']}% fell below the 90.0% Risk Manager threshold"
    )

    # 2. Recall Bar: >= 85% of legitimate winnable disputes must be captured
    assert metrics["recall_pct"] >= 85.0, (
        f"Recall {metrics['recall_pct']}% fell below the 85.0% Risk Manager threshold"
    )

    # 3. False Positive Rate: <= 10.0%
    assert metrics["false_positive_rate_pct"] <= 10.0, (
        f"False positive rate {metrics['false_positive_rate_pct']}% exceeded 10.0% threshold"
    )

    # 4. Financial ROI: Recovered capital must exceed wasted fees by at least 10x
    assert financials["roi_multiplier"] >= 10.0, (
        f"Financial ROI multiplier {financials['roi_multiplier']}x fell below 10.0x threshold"
    )

    # 5. Dataset adequacy: Benchmark must contain at least 50 held-out cases
    assert report["dataset_size"] >= 50, (
        f"Held-out dataset size {report['dataset_size']} is insufficient"
    )
