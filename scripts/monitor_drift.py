#!/usr/bin/env python3
"""
DayTone Model Drift Monitor
============================
Compares current model accuracy against a stored baseline and flags
potential drift. Run periodically (e.g. weekly via cron or CI).

Usage:
    python scripts/monitor_drift.py

Outputs:
    - Console summary with drift status
    - Updates app/ml/drift_baseline.json on first run
    - Exits with code 1 if drift exceeds threshold (useful in CI)
"""

import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH   = ROOT / "app" / "ml" / "model.pkl"
DATA_PATH    = ROOT / "app" / "ml" / "training_data.csv"
BASELINE_PATH = ROOT / "app" / "ml" / "drift_baseline.json"

FEATURE_NAMES = [
    "mood_score", "sleep_hours", "stress_level", "activity_done",
    "social_interaction", "sentiment_score", "avg_mood_7d",
    "avg_stress_7d", "avg_sleep_7d", "consecutive_bad_days",
    "mood_variability", "is_weekend",
]

DRIFT_THRESHOLD = 0.03   # Flag if accuracy drops >3 % from baseline
CLASSES = ["High", "Low", "Medium"]


def load_artifacts():
    if not MODEL_PATH.exists():
        sys.exit(f"[ERROR] Model not found: {MODEL_PATH}")
    if not DATA_PATH.exists():
        sys.exit(f"[ERROR] Data not found: {DATA_PATH}")

    with MODEL_PATH.open("rb") as f:
        payload = pickle.load(f)

    df = pd.read_csv(DATA_PATH)
    return payload["model"], df


def compute_metrics(model, df):
    X = df[FEATURE_NAMES].values
    y_true = df["burnout_risk"].values
    y_pred = model.predict(X)

    acc = accuracy_score(y_true, y_pred)
    f1s = f1_score(y_true, y_pred, labels=CLASSES, average=None, zero_division=0)
    macro_f1 = float(f1s.mean())
    return {
        "accuracy": round(float(acc), 6),
        "macro_f1": round(macro_f1, 6),
        "per_class_f1": {cls: round(float(v), 6) for cls, v in zip(CLASSES, f1s)},
        "n_samples": len(df),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    print("Loading model and data…")
    model, df = load_artifacts()

    current = compute_metrics(model, df)
    print(f"\nCurrent  — accuracy: {current['accuracy']:.1%}  macro-F1: {current['macro_f1']:.3f}  (n={current['n_samples']:,})")

    if not BASELINE_PATH.exists():
        BASELINE_PATH.write_text(json.dumps(current, indent=2))
        print(f"\n✓ No baseline found. Saved current metrics as baseline → {BASELINE_PATH.name}")
        return

    baseline = json.loads(BASELINE_PATH.read_text())
    acc_delta = current["accuracy"] - baseline["accuracy"]
    f1_delta  = current["macro_f1"] - baseline["macro_f1"]

    print(f"Baseline — accuracy: {baseline['accuracy']:.1%}  macro-F1: {baseline['macro_f1']:.3f}  (recorded {baseline['timestamp'][:10]})")
    print(f"\nDrift    — accuracy Δ: {acc_delta:+.1%}   macro-F1 Δ: {f1_delta:+.3f}")

    drifted = False
    if acc_delta < -DRIFT_THRESHOLD:
        print(f"\n⚠  DRIFT DETECTED: accuracy dropped {abs(acc_delta):.1%} (threshold {DRIFT_THRESHOLD:.0%})")
        print("   Action: retrain with `python -m app.ml.train`, then re-run this script to update baseline.")
        drifted = True
    else:
        print(f"\n✓  No significant drift detected (threshold {DRIFT_THRESHOLD:.0%}).")

    # Always write a drift report alongside baseline
    report = {
        "baseline": baseline,
        "current": current,
        "acc_delta": round(acc_delta, 6),
        "f1_delta": round(f1_delta, 6),
        "drifted": drifted,
        "threshold": DRIFT_THRESHOLD,
    }
    report_path = ROOT / "app" / "ml" / "drift_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"   Report saved → {report_path.name}")

    if drifted:
        sys.exit(1)


if __name__ == "__main__":
    main()
