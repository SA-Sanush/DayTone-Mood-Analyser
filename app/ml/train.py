import json
import logging
import pickle
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("train")

try:
    from app.ml.generate_data import generate
    from app.ml.predictor import FEATURE_NAMES
except ModuleNotFoundError:
    from generate_data import generate

    FEATURE_NAMES = [
        "mood_score",
        "sleep_hours",
        "stress_level",
        "activity_done",
        "social_interaction",
        "sentiment_score",
        "avg_mood_7d",
        "avg_stress_7d",
        "avg_sleep_7d",
        "consecutive_bad_days",
        "mood_variability",
        "is_weekend",
    ]


BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "training_data.csv"
MODEL_PATH = BASE / "model.pkl"
METRICS_PATH = BASE / "model_metrics.json"
META_PATH = BASE / "model_meta.json"


def load_training_data():
    if not DATA_PATH.exists():
        generate().to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)


def train():
    df = load_training_data()
    x = df[FEATURE_NAMES]
    y = df["burnout_risk"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)

    models = {
        "DecisionTree": DecisionTreeClassifier(random_state=42),
        "LogisticRegression": LogisticRegression(max_iter=800),
        "RandomForest": RandomForestClassifier(n_estimators=150, random_state=42),
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    best_name = None
    best_model = None
    best_acc = -1
    for name, model in models.items():
        # Cross-validation
        scores = cross_val_score(model, x, y, cv=cv, scoring="accuracy")
        logger.info(f"{name}: 5-fold cross-validation accuracy = {scores.mean():.2%} ± {scores.std():.2%}")

        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        accuracy = accuracy_score(y_test, predictions)
        results[name] = {
            "accuracy": accuracy,
            "report": classification_report(y_test, predictions, output_dict=True, zero_division=0),
        }
        logger.info(f"{name} holdout set accuracy: {accuracy:.2%}")
        logger.info(classification_report(y_test, predictions, zero_division=0))
        if accuracy > best_acc:
            best_name = name
            best_model = model
            best_acc = accuracy

    # Write active model
    payload = {"model": best_model, "name": best_name, "features": FEATURE_NAMES}
    with MODEL_PATH.open("wb") as model_file:
        pickle.dump(payload, model_file)

    # Write timestamped backup
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = BASE / f"model_{timestamp}.pkl"
    with backup_path.open("wb") as backup_file:
        pickle.dump(payload, backup_file)

    METRICS_PATH.write_text(json.dumps({"best": best_name, "accuracy": best_acc, "models": results}, indent=2))
    META_PATH.write_text(
        json.dumps(
            {
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "algorithm": best_name,
                "accuracy": best_acc,
                "n_samples": len(x_train) + len(x_test),
                "features": FEATURE_NAMES,
            },
            indent=2,
        )
    )
    logger.info(f"Best model: {best_name} ({best_acc:.2%})")
    logger.info(f"Saved model to {MODEL_PATH} and backup to {backup_path}")
    return best_name, best_acc


if __name__ == "__main__":
    train()
