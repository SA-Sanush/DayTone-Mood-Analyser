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
    # --- Sleep Deprivation (< 5 hours) ---
    {
        "condition": lambda sleep_hours, **_: sleep_hours < 5,
        "tip": lambda **_: "DO: Drink a warm glass of water or chamomile tea tonight and aim for a strict bedtime.",
    },
    {
        "condition": lambda sleep_hours, **_: sleep_hours < 5,
        "tip": lambda **_: "DON'T: Consuming caffeine after 2:00 PM today, as it will further disrupt your recovery.",
    },
    {
        "condition": lambda sleep_hours, **_: sleep_hours < 5,
        "tip": lambda **_: "DON'T: Using screens or scrolling for at least 45 minutes before attempting to sleep.",
    },
    # --- Mild Sleep Insufficiency (5 <= sleep < 7 hours) ---
    {
        "condition": lambda sleep_hours, **_: 5 <= sleep_hours < 7,
        "tip": lambda **_: "DO: Wind down 30 minutes earlier than usual tonight to build up sleep reserves.",
    },
    {
        "condition": lambda sleep_hours, **_: 5 <= sleep_hours < 7,
        "tip": lambda **_: "DON'T: Eating heavy meals or doing high-intensity workouts late in the evening.",
    },
    # --- High Stress (>= 4) ---
    {
        "condition": lambda stress_level, **_: stress_level >= 4,
        "tip": lambda **_: "DO: Practice a 5-minute guided box breathing session to reset your nervous system.",
    },
    {
        "condition": lambda stress_level, **_: stress_level >= 4,
        "tip": lambda **_: "DO: Plan 15 minutes of quiet reflection or mindfulness to declutter your thoughts.",
    },
    {
        "condition": lambda stress_level, **_: stress_level >= 4,
        "tip": lambda **_: "DON'T: Skipping meal breaks; take a full hour away from screens to rest.",
    },
    {
        "condition": lambda stress_level, **_: stress_level >= 4,
        "tip": lambda **_: "DON'T: Accepting new responsibilities today. Practice saying no gently.",
    },
    # --- Moderate Stress (3) ---
    {
        "condition": lambda stress_level, **_: stress_level == 3,
        "tip": lambda **_: "DO: Step away from your desk for a brief 10-minute stretching break.",
    },
    {
        "condition": lambda stress_level, **_: stress_level == 3,
        "tip": lambda **_: "DON'T: Drinking extra coffee or energy drinks; switch to water or herbal tea.",
    },
    # --- Isolation / Low Social Contact (social == 1) ---
    {
        "condition": lambda social_interaction, **_: social_interaction == 1,
        "tip": lambda **_: "DO: Send a quick message to a trusted friend or call a family member for a brief catch-up.",
    },
    {
        "condition": lambda social_interaction, **_: social_interaction == 1,
        "tip": lambda **_: "DON'T: Isolating yourself completely; even a short chat with a neighbor helps.",
    },
    # --- No Physical Activity ---
    {
        "condition": lambda activity_done, **_: not activity_done,
        "tip": lambda preferred_activity, **_: f"DO: Engage in a light 10-minute {preferred_activity} to boost your endorphins.",
    },
    {
        "condition": lambda activity_done, **_: not activity_done,
        "tip": lambda **_: "DON'T: Sitting for more than 90 consecutive minutes. Stand up and stretch.",
    },
    # --- High Burnout Risk ---
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.HIGH,
        "tip": lambda **_: "DO: Delegate non-essential work and discuss your current capacity with a manager or peer.",
    },
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.HIGH,
        "tip": lambda **_: "DO: Establish a firm, uncompromised boundary for when you stop working today.",
    },
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.HIGH,
        "tip": lambda **_: "DON'T: Checking work emails or messages after your established hours.",
    },
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.HIGH,
        "tip": lambda **_: "DON'T: Ignoring your physical exhaustion. Rest is productive and necessary.",
    },
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.HIGH,
        "tip": lambda **_: "DO: If you feel overwhelmed, seek guidance from a doctor or counselor. DayTone is not medical advice.",
    },
    # --- Medium Burnout Risk ---
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.MEDIUM,
        "tip": lambda **_: "DO: Set up 5-minute buffer spaces between meetings to avoid context-switching fatigue.",
    },
    {
        "condition": lambda burnout_risk, **_: burnout_risk == BurnoutRisk.MEDIUM,
        "tip": lambda **_: "DON'T: Packing your to-do list today; limit your focus to 3 key priorities.",
    },
    # --- Compound Condition: High Stress & Sleep Deprivation ---
    {
        "condition": lambda stress_level, sleep_hours, **_: stress_level >= 4
        and sleep_hours < 5,
        "tip": lambda **_: "DO: Dedicate 10 minutes to progressive muscle relaxation before bed to calm your mind.",
    },
    {
        "condition": lambda stress_level, sleep_hours, **_: stress_level >= 4
        and sleep_hours < 5,
        "tip": lambda **_: "DON'T: Working late or using high-sugar snacks to push through your tiredness.",
    },
    # --- Compound Condition: High Stress & No Activity ---
    {
        "condition": lambda stress_level, activity_done, **_: stress_level >= 4
        and not activity_done,
        "tip": lambda **_: "DO: Take a slow, quiet walk outdoors or practice a gentle yoga sequence to release tension.",
    },
    {
        "condition": lambda stress_level, activity_done, **_: stress_level >= 4
        and not activity_done,
        "tip": lambda **_: "DON'T: Staying indoors in a sedentary posture all day; movement is a stress reliever.",
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

    return tips or [
        "DO: Maintain your current healthy streaks and check-in daily.",
        "DON'T: Disrupting your established wellness habits.",
    ]
