import random
from pathlib import Path

import pandas as pd


OUTPUT = Path(__file__).resolve().parent / "training_data.csv"


def label_row(row):
    score = 0
    score += 2 if row["mood_score"] <= 2 else 0
    score += 2 if row["stress_level"] >= 4 else 0
    score += 1 if row["sleep_hours"] < 6 else 0
    score += 1 if row["activity_done"] == 0 else 0
    score += 1 if row["social_interaction"] == 1 else 0
    score += 1 if row["sentiment_score"] < -0.2 else 0
    score += 1 if row["consecutive_bad_days"] >= 3 else 0
    if score >= 5:
        return "High"
    if score >= 3:
        return "Medium"
    return "Low"


def generate(rows=300):
    random.seed(42)
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


if __name__ == "__main__":
    df = generate()
    df.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(df)} rows to {OUTPUT}")
