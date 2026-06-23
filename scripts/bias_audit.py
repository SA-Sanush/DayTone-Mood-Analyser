#!/usr/bin/env python3
"""
DayTone ML Bias & Fairness Audit Script
========================================
Evaluates the burnout predictor for systematic accuracy disparities
across synthetic demographic groups defined by stress and sleep levels.

Usage:
    python scripts/bias_audit.py

Requires:
    - app/ml/model.pkl  (trained model artifact)
    - app/ml/training_data.csv (training/evaluation dataset)
"""

import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "app" / "ml" / "model.pkl"
DATA_PATH  = ROOT / "app" / "ml" / "training_data.csv"

FEATURE_NAMES = [
    "mood_score", "sleep_hours", "stress_level", "activity_done",
    "social_interaction", "sentiment_score", "avg_mood_7d",
    "avg_stress_7d", "avg_sleep_7d", "consecutive_bad_days",
    "mood_variability", "is_weekend",
]
CLASSES = ["High", "Low", "Medium"]
BIAS_THRESHOLD = 0.05  # Flag if accuracy drops more than 5% below overall


def load_artifacts():
    if not MODEL_PATH.exists():
        sys.exit(f"[ERROR] Model not found at {MODEL_PATH}. Run: python -m app.ml.train")
    if not DATA_PATH.exists():
        sys.exit(f"[ERROR] Data not found at {DATA_PATH}.")

    with MODEL_PATH.open("rb") as f:
        payload = pickle.load(f)

    df = pd.read_csv(DATA_PATH)
    return payload["model"], df


def evaluate_group(model, df_group):
    """Return accuracy and per-class F1 for a data slice."""
    if df_group.empty:
        return None, {}

    X = df_group[FEATURE_NAMES].values
    y_true = df_group["burnout_risk"].values
    y_pred = model.predict(X)

    acc = accuracy_score(y_true, y_pred)
    f1s = f1_score(y_true, y_pred, labels=CLASSES, average=None, zero_division=0)
    return acc, dict(zip(CLASSES, f1s))


def define_groups(df):
    """Return a list of (group_label, sub-dataframe) tuples."""
    groups = []

    # ── Stress quintile groups ────────────────────────────────────────────
    stress_bins = [
        ("Stress: Very Low (1)",  df[df["stress_level"] == 1]),
        ("Stress: Low (2)",       df[df["stress_level"] == 2]),
        ("Stress: Medium (3)",    df[df["stress_level"] == 3]),
        ("Stress: High (4)",      df[df["stress_level"] == 4]),
        ("Stress: Very High (5)", df[df["stress_level"] == 5]),
    ]
    groups.extend(stress_bins)

    # ── Sleep groups ──────────────────────────────────────────────────────
    sleep_bins = [
        ("Sleep: <6h",  df[df["sleep_hours"] < 6]),
        ("Sleep: 6-7h", df[(df["sleep_hours"] >= 6) & (df["sleep_hours"] < 7)]),
        ("Sleep: 7-8h", df[(df["sleep_hours"] >= 7) & (df["sleep_hours"] < 8)]),
        ("Sleep: 8h+",  df[df["sleep_hours"] >= 8]),
    ]
    groups.extend(sleep_bins)

    # ── Activity groups ───────────────────────────────────────────────────
    groups.append(("Activity: Done",     df[df["activity_done"] == 1]))
    groups.append(("Activity: Not Done", df[df["activity_done"] == 0]))

    # ── Social interaction groups ─────────────────────────────────────────
    groups.append(("Social: Isolated (1)",    df[df["social_interaction"] == 1]))
    groups.append(("Social: Moderate (2)",    df[df["social_interaction"] == 2]))
    groups.append(("Social: Connected (3)",   df[df["social_interaction"] == 3]))

    return groups


def print_results(overall_acc, group_results):
    SEP = "─" * 85
    print(f"\n{'DayTone ML Bias & Fairness Audit':^85}")
    print(SEP)
    print(f"{'Group':<35} {'N':>6} {'Accuracy':>10} {'F1-High':>8} {'F1-Low':>8} {'F1-Med':>8}  Flag")
    print(SEP)

    flagged = []
    for label, n, acc, f1s in group_results:
        if acc is None:
            print(f"  {label:<33} {'0':>6} {'N/A':>10}")
            continue

        flag = ""
        if (overall_acc - acc) > BIAS_THRESHOLD:
            flag = "⚠ BIAS_FLAG"
            flagged.append(label)

        f_high = f"{f1s.get('High', 0.0):.3f}"
        f_low  = f"{f1s.get('Low',  0.0):.3f}"
        f_med  = f"{f1s.get('Medium', 0.0):.3f}"

        print(f"  {label:<33} {n:>6} {acc:>10.1%} {f_high:>8} {f_low:>8} {f_med:>8}  {flag}")

    print(SEP)
    print(f"  {'OVERALL'::<33} {'-':>6} {overall_acc:>10.1%}")
    print(SEP)

    if flagged:
        print(f"\n⚠  {len(flagged)} group(s) flagged (accuracy >{BIAS_THRESHOLD*100:.0f}% below overall):")
        for g in flagged:
            print(f"   - {g}")
    else:
        print("\n✓  No bias flags detected. All groups within acceptable threshold.")

    print()


def main():
    print("Loading model and data...")
    model, df = load_artifacts()

    # Overall evaluation
    overall_acc, _ = evaluate_group(model, df)
    print(f"Dataset: {len(df):,} rows | Overall accuracy: {overall_acc:.1%}\n")

    # Group evaluations
    groups = define_groups(df)
    group_results = []
    for label, df_group in groups:
        acc, f1s = evaluate_group(model, df_group)
        group_results.append((label, len(df_group), acc, f1s))

    print_results(overall_acc, group_results)


if __name__ == "__main__":
    main()
