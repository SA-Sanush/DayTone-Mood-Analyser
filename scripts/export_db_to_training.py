#!/usr/bin/env python
"""
export_db_to_training.py

Extracts real user logs from the active Flask database, builds the 12-feature
vectors using historical logs, and outputs/merges them into app/ml/training_data.csv.
This allows the project to transition from synthetic-only training to real-user training.
"""

import sys
import os
import argparse
import pandas as pd
from pathlib import Path

# Add project root to path so we can import app modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db
from app.models import MoodLog
from app.ml.predictor import build_features, FEATURE_NAMES

DATA_PATH = project_root / "app" / "ml" / "training_data.csv"


def extract_real_logs(app):
    with app.app_context():
        # Query all logs ordered by user and date to ensure build_features has context
        logs = MoodLog.query.order_by(MoodLog.user_id, MoodLog.log_date.asc()).all()
        if not logs:
            print("No real user logs found in the database.")
            return []

        print(f"Found {len(logs)} real user logs in the database. Constructing features...")
        rows = []
        success_count = 0
        
        for log in logs:
            try:
                # build_features queries preceding logs for the rolling 7-day averages
                features = build_features(
                    user_id=log.user_id,
                    log_date=log.log_date,
                    mood_score=log.mood_score,
                    sleep_hours=log.sleep_hours,
                    stress_level=log.stress_level,
                    activity_done=log.activity_done,
                    social_interaction=log.social_interaction,
                    sentiment_score=log.sentiment_score
                )
                
                # Append target label
                features["burnout_risk"] = log.burnout_risk
                rows.append(features)
                success_count += 1
            except Exception as e:
                # If there are indexing issues or invalid logs, skip them
                continue

        print(f"Successfully constructed feature vectors for {success_count}/{len(logs)} logs.")
        return rows


def main():
    parser = argparse.ArgumentParser(
        description="Compile real user logs from the database into the ML training dataset."
    )
    parser.add_argument(
        "--mode",
        choices=["merge", "replace"],
        default="merge",
        help=(
            "merge (default): Combine real logs with synthetic baseline to avoid cold-start sparsity. "
            "replace: Overwrite the training file using ONLY real database logs (requires at least 50 logs)."
        ),
    )
    args = parser.parse_args()

    app = create_app()
    real_rows = extract_real_logs(app)
    
    if not real_rows:
        print("Extraction completed. No database logs exported. No changes made.")
        sys.exit(0)

    real_df = pd.DataFrame(real_rows)

    if args.mode == "replace":
        if len(real_df) < 50:
            print(
                f"WARNING: Only {len(real_df)} real logs found. Replacing the training set with "
                "under 50 samples can lead to severe overfitting. Merging instead."
            )
            args.mode = "merge"
        else:
            real_df.to_csv(DATA_PATH, index=False)
            print(f"Successfully replaced dataset. Wrote {len(real_df)} real logs to {DATA_PATH}.")

    if args.mode == "merge":
        # Load synthetic baseline
        if DATA_PATH.exists():
            base_df = pd.read_csv(DATA_PATH)
            # Remove any existing rows matching the user_id profile to avoid duplicates (optional)
            combined_df = pd.concat([base_df, real_df], ignore_index=True)
            combined_df.to_csv(DATA_PATH, index=False)
            print(
                f"Successfully merged data. Appended {len(real_df)} real logs to the existing "
                f"dataset (Total rows: {len(combined_df)})."
            )
        else:
            real_df.to_csv(DATA_PATH, index=False)
            print(f"No existing training_data.csv found. Wrote {len(real_df)} real logs to {DATA_PATH}.")

    print("\nNext steps:")
    print("1. Retrain the model on the updated dataset:")
    print("   python -m app.ml.train")
    print("2. Run the fairness audit on real-world distributions:")
    print("   python scripts/bias_audit.py")
    print("3. Check for drift against the baseline model:")
    print("   python scripts/monitor_drift.py")


if __name__ == "__main__":
    main()
