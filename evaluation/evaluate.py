"""
DisputeSentinel AI — Held-Out Test Set Risk Evaluation Benchmark
Evaluates the entire multi-agent pipeline against a strictly held-out test dataset
using standard scikit-learn metrics and Razorpay-specific financial cost models.
"""

from pathlib import Path
import json

from evaluation.pipeline_adapter import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = ROOT / "dataset" / "held_out_test.csv"
OUTPUT_REPORT_PATH = Path(__file__).parent / "benchmark_report.json"

AUTO_CONTEST_COST = 1500  # ₹1,500 standard Razorpay dispute processing fee

def run_held_out_evaluation():
    # 1. Validate dataset existence and size requirement
    assert TEST_PATH.exists(), f"Held-out test dataset not found at: {TEST_PATH}"
    
    rows = []
    try:
        import pandas as pd
        df_raw = pd.read_csv(TEST_PATH)
        rows = df_raw.to_dict(orient="records")
    except Exception:
        import csv
        with open(TEST_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    assert len(rows) >= 50, f"Held-out test set is too small: {len(rows)} cases (minimum 50 required)"

    print(f"Evaluation set: {len(rows)} cases")
    print("Dataset role: HELD-OUT TEST SET (Never seen during development/tuning)")
    print("Dataset type: Synthetic benchmark dataset for reproducible evaluation\n")

    # 2. Execute full pipeline through evaluation adapter
    y_true = []
    y_pred = []
    dispute_amounts = []
    
    for row in rows:
        case_dict = dict(row)
        res = evaluate_case(case_dict)
        ground_truth_val = int(case_dict.get("ground_truth", 0))
        predicted_val = int(res["predicted"])
        amount_val = int(float(case_dict.get("dispute_amount", 0)))

        y_true.append(ground_truth_val)
        y_pred.append(predicted_val)
        dispute_amounts.append(amount_val)

    # 3. Calculate Scikit-Learn Metrics (with native fallback)
    try:
        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            confusion_matrix,
        )
        import numpy as np
        y_true_arr = np.array(y_true)
        y_pred_arr = np.array(y_pred)
        tn, fp, fn, tp = confusion_matrix(y_true_arr, y_pred_arr, labels=[0, 1]).ravel()
        precision = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
        recall = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
        f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))
        accuracy = float(accuracy_score(y_true_arr, y_pred_arr))
    except Exception:
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0.0

    fpr = float(fp / (fp + tn)) if (fp + tn) else 0.0

    # 4. Explicit Razorpay False-Positive & Financial Cost Model
    false_positive_cost = int(fp * AUTO_CONTEST_COST)
    
    # Capital calculation: Recovered is sum of TP dispute amounts (in INR)
    recovered_capital = int(sum(amt for amt, yt, yp in zip(dispute_amounts, y_true, y_pred) if yt == 1 and yp == 1))
    total_disputed_capital = int(sum(dispute_amounts))
    net_value = int(recovered_capital - false_positive_cost)
    roi_multiplier = round(recovered_capital / (false_positive_cost + 1), 1) if false_positive_cost > 0 else 50.0

    # 5. Output results
    print("=" * 60)
    print(" [*] DISPUTESENTINEL AI - RISK MANAGER EVALUATION REPORT")
    print("=" * 60)
    print(f" Precision: {precision:.2%}")
    print(f" Recall:    {recall:.2%}")
    print(f" F1:        {f1:.2%}")
    print(f" Accuracy:  {accuracy:.2%}")
    print(f" FPR:       {fpr:.2%}")
    print("-" * 60)
    print(f" Confusion Matrix: [TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}]")
    print("-" * 60)
    print(" FINANCIAL IMPACT AUDIT:")
    print(f"  - Total Disputed Capital:  Rs {total_disputed_capital:,}")
    print(f"  - Recovered Capital (TP):  Rs {recovered_capital:,}")
    print(f"  - False Positive Fee Cost: Rs {false_positive_cost:,} ({fp} FP cases @ Rs {AUTO_CONTEST_COST}/dispute)")
    print(f"  - Net Value Saved:         Rs {net_value:,}")
    print(f"  - Net ROI Multiplier:      {roi_multiplier}x")
    print("=" * 60 + "\n")

    report_payload = {
        "dataset_role": "HELD-OUT TEST SET",
        "dataset_type": "Synthetic benchmark dataset for reproducible evaluation",
        "dataset_size": len(rows),
        "metrics": {
            "precision_pct": round(precision * 100, 2),
            "recall_pct": round(recall * 100, 2),
            "f1_score": round(f1, 4),
            "accuracy_pct": round(accuracy * 100, 2),
            "false_positive_rate_pct": round(fpr * 100, 2)
        },
        "confusion_matrix": {
            "true_positives": int(tp),
            "false_positives": int(fp),
            "true_negatives": int(tn),
            "false_negatives": int(fn)
        },
        "financial_impact": {
            "false_positive_count": int(fp),
            "false_positive_cost_inr": false_positive_cost,
            "true_positive_recovered_inr": recovered_capital,
            "total_disputed_capital_inr": total_disputed_capital,
            "net_value_saved_inr": net_value,
            "roi_multiplier": roi_multiplier
        }
    }

    with open(OUTPUT_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)

    return report_payload

if __name__ == "__main__":
    run_held_out_evaluation()
