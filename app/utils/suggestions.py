from flask import current_app, has_app_context

from app.constants import BurnoutRisk


CRISIS_RESOURCES = {
    "US": "Call or text 988 for the Suicide & Crisis Lifeline.",
    "IN": "Visit https://findahelpline.com/in for crisis support options in India.",
    "UK": "Call Samaritans at 116 123 or visit https://www.samaritans.org.",
    "GLOBAL": "Visit https://findahelpline.com to find crisis support near you.",
}


def crisis_resource_text():
    country = "GLOBAL"
    if has_app_context():
        country = current_app.config.get("COUNTRY", "GLOBAL")
    return CRISIS_RESOURCES.get(str(country).upper(), CRISIS_RESOURCES["GLOBAL"])


RULES = [
    {
        "condition": lambda sleep_hours, **_: sleep_hours < 5,
        "tip": lambda **_: "You slept very little. Aim for 7-8 hours tonight and set a fixed bedtime alarm.",
    },
    {
        "condition": lambda sleep_hours, **_: 5 <= sleep_hours < 7,
        "tip": lambda **_: "Try getting to bed 30 minutes earlier tonight to improve your sleep score.",
    },
    {
        "condition": lambda stress_level, **_: stress_level >= 4,
        "tip": lambda **_: "Your stress is high. Try a 5-minute box breathing exercise right now.",
    },
    {
        "condition": lambda social_interaction, **_: social_interaction == 1,
        "tip": lambda **_: "You had no social contact today. Send a quick message to someone you trust.",
    },
    {
        "condition": lambda activity_done, **_: not activity_done,
        "tip": lambda preferred_activity, **_: f"No activity today. A 10-minute {preferred_activity} can help lift your mood.",
    },
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.HIGH,
        "tip": lambda **_: "High burnout risk detected. DayTone is not medical advice; speak to a trusted person or counsellor today.",
    },
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.HIGH,
        "tip": lambda **_: f"If you feel unsafe or may harm yourself, contact local emergency services now. {crisis_resource_text()}",
    },
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.HIGH,
        "tip": lambda **_: "Avoid heavy workload tomorrow. Rest is productive.",
    },
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.MEDIUM,
        "tip": lambda **_: "You are showing medium burnout signs. Take short breaks every 45 minutes.",
    },
]


def get_suggestions(
    burnout_risk: str,
    sleep_hours: float,
    stress_level: int,
    social_interaction: int,
    activity_done: bool,
    preferred_activity: str = "Walk",
) -> list[str]:
    """Evaluate context against set rules to generate actionable suggestions."""
    context = {
        "burnout_risk": burnout_risk,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "social_interaction": social_interaction,
        "activity_done": activity_done,
        "preferred_activity": preferred_activity,
    }
    tips = []
    for rule in RULES:
        try:
            if rule["condition"](**context):
                tips.append(rule["tip"](**context))
        except Exception:
            continue

    return tips or ["Great day. Keep maintaining your healthy habits."]
