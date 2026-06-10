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


def get_suggestions(
    burnout_risk,
    sleep_hours,
    stress_level,
    social_interaction,
    activity_done,
    preferred_activity="Walk",
):
    tips = []

    if sleep_hours < 5:
        tips.append("You slept very little. Aim for 7-8 hours tonight and set a fixed bedtime alarm.")
    elif sleep_hours < 7:
        tips.append("Try getting to bed 30 minutes earlier tonight to improve your sleep score.")

    if stress_level >= 4:
        tips.append("Your stress is high. Try a 5-minute box breathing exercise right now.")

    if social_interaction == 1:
        tips.append("You had no social contact today. Send a quick message to someone you trust.")

    if not activity_done:
        tips.append(f"No activity today. A 10-minute {preferred_activity} can help lift your mood.")

    if burnout_risk == BurnoutRisk.HIGH:
        tips.append("High burnout risk detected. DayTone is not medical advice; speak to a trusted person or counsellor today.")
        tips.append(f"If you feel unsafe or may harm yourself, contact local emergency services now. {crisis_resource_text()}")
        tips.append("Avoid heavy workload tomorrow. Rest is productive.")
    elif burnout_risk == BurnoutRisk.MEDIUM:
        tips.append("You are showing medium burnout signs. Take short breaks every 45 minutes.")

    return tips or ["Great day. Keep maintaining your healthy habits."]
