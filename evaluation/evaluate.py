"""
DisputeSentinel AI — Risk Evaluation Benchmark Harness
Measures Precision, Recall, False Positive Rate (FPR), and Financial Impact
on a held-out dataset of dispute cases to satisfy Risk Manager evaluation requirements.
"""

import os
import csv
import json
from pathlib import Path
from typing import Dict, Any, List

def calculate_dispute_score(row: Dict[str, str]) -> Dict[str, Any]:
    """
    Simulates the multi-modal scoring pipeline logic:
    Weights courier delivery proof, OCR signature match, IP geolocation match,
    device reuse history, and dispute filing timing.
    """
    score = 50.0  # Base prior
    
    delivery_status = row.get("delivery_status", "").upper()
    pod_sig = row.get("pod_signature_detected", "").lower() == "true"
    pod_name = row.get("pod_name_match", "").lower() == "true"
    ocr_conf = float(row.get("ocr_confidence", "0.0") or 0.0)
    ip_match = row.get("ip_billing_match", "").lower() == "true"
    device_count = int(row.get("device_reuse_count", "0") or 0)
    days_to_filing = int(row.get("days_to_filing", "0") or 0)
    reason = row.get("reason_code", "")

    # Multi-modal Signal Attribution
    if delivery_status == "DELIVERED":
        score += 15.0
        if pod_sig and pod_name and ocr_conf >= 0.80:
            score += 25.0 * ocr_conf
        elif not pod_sig:
            score -= 20.0
    else:
        score -= 40.0

    if ip_match:
        score += 10.0
    else:
        score -= 15.0

    if device_count >= 3:
        score += min(15.0, device_count * 2.5)
    elif device_count == 0:
        score -= 10.0

    if days_to_filing > 10 and reason == "product_not_delivered":
        score -= 15.0

    # Bounds
    win_probability = max(5.0, min(98.0, round(score, 1)))

    # Policy Decision Gate
    # Threshold for Auto-Contest is win_probability >= 65
    # Threshold for Human Review is 45 <= win_probability < 65
    # Below 45 is Accept Loss
    if win_probability >= 65.0:
        predicted_action = "AUTO_CONTEST"
    elif win_probability >= 45.0:
        predicted_action = "NEEDS_REVIEW"
    else:
        predicted_action = "ACCEPT_LOSS"

    return {
        "win_probability": win_probability,
        "predicted_action": predicted_action,
        "should_contest": predicted_action in ["AUTO_CONTEST", "NEEDS_REVIEW"]
    }

def run_evaluation(csv_path: str = None) -> Dict[str, Any]:
    if not csv_path:
        csv_path = Path(__file__).parent.parent / "dataset" / "disputes.csv"

    tp = 0  # True Positive: Contested and actually WON
    fp = 0  # False Positive: Contested but actually LOST (Wasted fee & capital)
    tn = 0  # True Negative: Accepted loss and was actually LOST (Saved fees)
    fn = 0  # False Negative: Accepted loss but was actually WON (Missed recovery)

    total_capital = 0
    contested_capital = 0
    recovered_capital = 0
    false_positive_cost = 0  # ₹1500 Razorpay gateway fee + lost disputed amount

    GATEWAY_DISPUTE_FEE = 1500  # ₹1,500 standard chargeback processing fee

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amount = float(row.get("amount_inr", "0") or 0.0)
            actual = row.get("actual_outcome", "").upper()
            pred = calculate_dispute_score(row)

            total_capital += amount
            should_contest = pred["should_contest"]

            if should_contest and actual == "WON":
                tp += 1
                contested_capital += amount
                recovered_capital += amount
            elif should_contest and actual == "LOST":
                fp += 1
                contested_capital += amount
                false_positive_cost += GATEWAY_DISPUTE_FEE  # Incurred fee on lost dispute
            elif not should_contest and actual == "LOST":
                tn += 1
            elif not should_contest and actual == "WON":
                fn += 1

    total_samples = tp + fp + tn + fn
    precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0.0
    recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    fpr = (fp / (fp + tn)) * 100 if (fp + tn) > 0 else 0.0
    accuracy = ((tp + tn) / total_samples) * 100 if total_samples > 0 else 0.0

    roi_multiplier = (recovered_capital / (false_positive_cost + 1)) if false_positive_cost > 0 else 50.0

    report = {
        "dataset_size": total_samples,
        "metrics": {
            "precision_pct": round(precision, 2),
            "recall_pct": round(recall, 2),
            "f1_score": round(f1, 2),
            "false_positive_rate_pct": round(fpr, 2),
            "accuracy_pct": round(accuracy, 2)
        },
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn
        },
        "financial_impact_inr": {
            "total_disputed_capital": round(total_capital, 2),
            "contested_capital": round(contested_capital, 2),
            "recovered_capital": round(recovered_capital, 2),
            "false_positive_fee_waste": round(false_positive_cost, 2),
            "net_capital_saved": round(recovered_capital - false_positive_cost, 2),
            "roi_multiplier": round(roi_multiplier, 1)
        }
    }

    return report

def print_evaluation_report(report: Dict[str, Any]):
    m = report["metrics"]
    cm = report["confusion_matrix"]
    fin = report["financial_impact_inr"]

    print("\n" + "="*60)
    print(" [*] DISPUTESENTINEL AI - RISK EVALUATION BENCHMARK REPORT")
    print("="*60)
    print(f" Dataset Size Tested:      {report['dataset_size']} held-out dispute cases")
    print(f" Precision (Win Accuracy): {m['precision_pct']}%  (Target: >= 90.0%)")
    print(f" Recall (Coverage):        {m['recall_pct']}%  (Target: >= 85.0%)")
    print(f" F1-Score:                 {m['f1_score']}")
    print(f" False Positive Rate:      {m['false_positive_rate_pct']}%  (Target: <= 5.0%)")
    print(f" Accuracy:                 {m['accuracy_pct']}%")
    print("-" * 60)
    print(f" Confusion Matrix: [TP: {cm['true_positives']}, FP: {cm['false_positives']}, TN: {cm['true_negatives']}, FN: {cm['false_negatives']}]")
    print("-" * 60)
    print(" FINANCIAL IMPACT & ROI AUDIT:")
    print(f"  - Total Disputed Capital: Rs {fin['total_disputed_capital']:,.2f}")
    print(f"  - Capital Contested:     Rs {fin['contested_capital']:,.2f}")
    print(f"  - Capital Recovered:     Rs {fin['recovered_capital']:,.2f}")
    print(f"  - Dispute Fee Waste:     Rs {fin['false_positive_fee_waste']:,.2f}")
    print(f"  - Net Saved Capital:     Rs {fin['net_capital_saved']:,.2f}")
    print(f"  - Net ROI Multiplier:    {fin['roi_multiplier']}x")
    print("="*60 + "\n")

if __name__ == "__main__":
    rep = run_evaluation()
    print_evaluation_report(rep)
    
    # Save output to JSON
    output_path = Path(__file__).parent / "benchmark_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
