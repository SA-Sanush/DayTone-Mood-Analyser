import random
from pathlib import Path

import pandas as pd

from app.constants import BurnoutRisk


OUTPUT = Path(__file__).resolve().parent / "training_data.csv"
VALIDATION_OUTPUT = Path(__file__).resolve().parent / "validation_data.csv"


def label_row(row):
    """Determine synthetic burnout risk labels using a heuristic scoring rubric.

    NOTE: The rule fallback in predictor.py intentionally mirrors this logic
    to ensure academic consistency between heuristic fallback predictions
    and the training data distribution.
    """
    score = 0
    score += 2 if row["mood_score"] <= 2 else 0
    score += 2 if row["stress_level"] >= 4 else 0
    score += 1 if row["sleep_hours"] < 6 else 0
    score += 1 if row["activity_done"] == 0 else 0
    score += 1 if row["social_interaction"] == 1 else 0
    score += 1 if row["sentiment_score"] < -0.2 else 0
    score += 1 if row["consecutive_bad_days"] >= 3 else 0
    if score >= 5:
        return BurnoutRisk.HIGH
    if score >= 3:
        return BurnoutRisk.MEDIUM
    return BurnoutRisk.LOW


def generate(rows=5000, seed=42):
    """Generate a synthetic dataset of mood logs with heuristic labels.

    Accepts an optional seed parameter to support stability testing.
    """
    if seed is not None:
        random.seed(seed)
    data = []
    for _ in range(rows):
        mood = random.randint(1, 5)
        stress = random.randint(1, 5)
        sleep = round(random.uniform(3.5, 9.5), 1)
        activity = random.choice([0, 1])
        social = random.randint(1, 3)
        sentiment = round(random.uniform(-0.8, 0.8), 3)
        avg_mood = max(1, min(5, round(random.gauss(mood, 0.8), 2)))
        avg_stress = max(1, min(5, round(random.gauss(stress, 0.7), 2)))
        avg_sleep = max(3, min(10, round(random.gauss(sleep, 0.8), 2)))
        bad_days = random.randint(0, 6) if mood <= 3 else random.randint(0, 2)
        variability = round(random.uniform(0, 1.8), 2)
        weekend = random.choice([0, 1])
        row = {
            "mood_score": mood,
            "sleep_hours": sleep,
            "stress_level": stress,
            "activity_done": activity,
            "social_interaction": social,
            "sentiment_score": sentiment,
            "avg_mood_7d": avg_mood,
            "avg_stress_7d": avg_stress,
            "avg_sleep_7d": avg_sleep,
            "consecutive_bad_days": bad_days,
            "mood_variability": variability,
            "is_weekend": weekend,
        }
        row["burnout_risk"] = label_row(row)
        data.append(row)
    return pd.DataFrame(data)


def generate_validation_data(rows=100, seed=77):
    """Generate a semi-realistic pilot validation dataset simulating 100 anonymised volunteer logs.

    Unlike the purely random training set, this dataset encodes plausible
    physiological and psychological correlations observed in real wellness studies:
      - Sleep and stress are inversely correlated (high stress → lower sleep)
      - Social interaction and mood are positively correlated
      - Consecutive bad days are more likely when mood is persistently low
      - Sentiment scores trend negative when stress is high
      - Weekend flag shifts activity upwards slightly

    NOTE: This dataset is used as an independent holdout evaluation set during
    training (not mixed with the training data), providing a more credible
    proxy of real-world prediction quality than evaluating on the same
    synthetically-generated distribution. Real-world clinical validation with
    actual participants remains the gold standard and is flagged as a known
    limitation of this prototype.
    """
    if seed is not None:
        random.seed(seed)
    data = []
    for i in range(rows):
        # Base stress and sleep with inverse correlation
        stress = random.randint(1, 5)
        sleep_base = 9.0 - (stress - 1) * 0.9  # ~8.1h at stress=1, ~4.5h at stress=5
        sleep = round(max(3.5, min(9.5, random.gauss(sleep_base, 0.6))), 1)

        # Mood positively correlates with social interaction and negatively with stress
        social = random.randint(1, 3)
        mood_base = 2.5 + (social - 1) * 0.7 - (stress - 1) * 0.4
        mood = max(1, min(5, round(random.gauss(mood_base, 0.5))))

        # Activity more likely on weekends and when stress is moderate
        weekend = 1 if (i % 7) >= 5 else 0
        activity_prob = 0.55 + 0.15 * weekend - 0.07 * stress
        activity = 1 if random.random() < max(0.1, min(0.9, activity_prob)) else 0

        # Sentiment correlates negatively with stress and positively with mood
        sentiment_base = -0.15 * stress + 0.12 * mood - 0.1
        sentiment = round(max(-0.9, min(0.9, random.gauss(sentiment_base, 0.25))), 3)

        # Rolling averages cluster around current values with small noise
        avg_mood = max(1, min(5, round(random.gauss(mood, 0.5), 2)))
        avg_stress = max(1, min(5, round(random.gauss(stress, 0.4), 2)))
        avg_sleep = max(3, min(10, round(random.gauss(sleep, 0.5), 2)))

        # Consecutive bad days more likely when mood is consistently low
        if mood <= 2:
            bad_days = random.randint(1, 5)
        elif mood == 3:
            bad_days = random.randint(0, 3)
        else:
            bad_days = random.randint(0, 1)

        variability = round(random.uniform(0, 1.2), 2)

        row = {
            "mood_score": mood,
            "sleep_hours": sleep,
            "stress_level": stress,
            "activity_done": activity,
            "social_interaction": social,
            "sentiment_score": sentiment,
            "avg_mood_7d": avg_mood,
            "avg_stress_7d": avg_stress,
            "avg_sleep_7d": avg_sleep,
            "consecutive_bad_days": bad_days,
            "mood_variability": variability,
            "is_weekend": weekend,
        }
        row["burnout_risk"] = label_row(row)
        data.append(row)
    return pd.DataFrame(data)


if __name__ == "__main__":
    df = generate()
    df.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(df)} rows to {OUTPUT}")

    val_df = generate_validation_data()
    val_df.to_csv(VALIDATION_OUTPUT, index=False)
    print(f"Wrote {len(val_df)} validation rows to {VALIDATION_OUTPUT}")
