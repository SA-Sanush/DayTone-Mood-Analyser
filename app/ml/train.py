import json
import logging
import joblib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("train")

try:
    from app.ml.generate_data import generate, generate_validation_data
    from app.ml.predictor import FEATURE_NAMES
except ModuleNotFoundError:
    from generate_data import generate, generate_validation_data

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
VALIDATION_PATH = BASE / "validation_data.csv"
MODEL_PATH = BASE / "model.pkl"
METRICS_PATH = BASE / "model_metrics.json"
META_PATH = BASE / "model_meta.json"

CLASSES = ["High", "Low", "Medium"]


def load_training_data():
    if not DATA_PATH.exists():
        generate().to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)


def load_validation_data():
    """Load the semi-real pilot validation dataset, generating it if absent."""
    if not VALIDATION_PATH.exists():
        generate_validation_data().to_csv(VALIDATION_PATH, index=False)
    return pd.read_csv(VALIDATION_PATH)


def _build_confusion_matrix(y_true, y_pred):
    """Return confusion matrix as a nested dict keyed by actual → predicted class."""
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    result = {}
    for i, actual in enumerate(CLASSES):
        result[actual] = {CLASSES[j]: int(cm[i][j]) for j in range(len(CLASSES))}
    return result


def train():
    df = load_training_data()
    val_df = load_validation_data()

    x = df[FEATURE_NAMES]
    y = df["burnout_risk"]
    x_val = val_df[FEATURE_NAMES]
    y_val = val_df["burnout_risk"]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

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
        # Cross-validation on synthetic training distribution
        scores = cross_val_score(model, x, y, cv=cv, scoring="accuracy")
        logger.info(
            f"{name}: 5-fold cross-validation accuracy = {scores.mean():.2%} ± {scores.std():.2%}"
        )

        model.fit(x_train, y_train)

        # Synthetic holdout evaluation
        predictions = model.predict(x_test)
        accuracy = accuracy_score(y_test, predictions)
        report = classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        )
        logger.info(f"{name} holdout set accuracy: {accuracy:.2%}")
        logger.info(classification_report(y_test, predictions, zero_division=0))

        # Semi-real validation evaluation (independent holdout set)
        val_predictions = model.predict(x_val)
        val_accuracy = accuracy_score(y_val, val_predictions)
        val_report = classification_report(
            y_val, val_predictions, output_dict=True, zero_division=0
        )
        val_cm = _build_confusion_matrix(y_val, val_predictions)
        logger.info(f"{name} semi-real validation accuracy: {val_accuracy:.2%}")
        logger.info(f"{name} semi-real validation confusion matrix: {val_cm}")

        results[name] = {
            "accuracy": accuracy,
            "report": report,
            "cv_mean": round(float(scores.mean()), 4),
            "cv_std": round(float(scores.std()), 4),
            "validation": {
                "accuracy": round(float(val_accuracy), 4),
                "report": val_report,
                "confusion_matrix": val_cm,
                "n_samples": len(y_val),
                "note": (
                    "Evaluated on a 100-sample semi-real pilot dataset with physiologically "
                    "plausible correlations (inverse sleep/stress, positive social/mood). "
                    "Real-world clinical validation with consenting participants remains a "
                    "known limitation of this prototype."
                ),
            },
        }

        if accuracy > best_acc:
            best_name = name
            best_model = model
            best_acc = accuracy

    # Write active model
    payload = {"model": best_model, "name": best_name, "features": FEATURE_NAMES}
    with MODEL_PATH.open("wb") as model_file:
        joblib.dump(payload, model_file)

    # Write timestamped backup
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = BASE / f"model_{timestamp}.pkl"
    with backup_path.open("wb") as backup_file:
        joblib.dump(payload, backup_file)

    METRICS_PATH.write_text(
        json.dumps(
            {"best": best_name, "accuracy": best_acc, "models": results}, indent=2
        )
    )
    META_PATH.write_text(
        json.dumps(
            {
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "algorithm": best_name,
                "accuracy": best_acc,
                "n_samples": len(x_train) + len(x_test),
                "validation_n_samples": len(y_val),
                "features": FEATURE_NAMES,
                "known_limitations": [
                    "Trained on synthetically generated data with heuristic labels — not on real clinical data.",
                    "Validation uses semi-real pilot data with plausible correlations, not actual volunteer logs.",
                    "VADER sentiment analysis lacks nuanced context, sarcasm, or domain-specific distress language.",
                    "No longitudinal feedback loop; model does not learn from post-prediction outcomes.",
                    "Real-world deployment requires IRB-approved data collection and clinical collaboration.",
                ],
            },
            indent=2,
        )
    )
    logger.info(f"Best model: {best_name} ({best_acc:.2%})")
    logger.info(f"Saved model to {MODEL_PATH} and backup to {backup_path}")
    return best_name, best_acc


if __name__ == "__main__":
    train()
