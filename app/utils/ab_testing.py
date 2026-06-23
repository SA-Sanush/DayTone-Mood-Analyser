"""
A/B Testing utilities for DayTone.

Assigns users to experiment variants using a deterministic hash so the
same user always sees the same variant without storing anything in the DB.
Results are logged so they can be analysed offline.

Usage example in a route:
    from app.utils.ab_testing import get_variant, log_conversion

    variant = get_variant(current_user.id, "suggestion_layout")
    # variant is "control" or "treatment"
"""

import hashlib
import logging

logger = logging.getLogger(__name__)

# ── Experiment registry ───────────────────────────────────────────────────────
# Each entry: experiment_name -> {"variants": [...], "weights": [...]}
# weights must sum to 1.0; omit to get equal split.
EXPERIMENTS = {
    "suggestion_layout": {
        "variants": ["control", "treatment"],
        "description": "control=card list, treatment=prioritised top-3 banner",
    },
    "dashboard_tip_position": {
        "variants": ["below_orb", "inline_drivers"],
        "description": "Where the daily tip appears on the dashboard",
    },
    "onboarding_cta_copy": {
        "variants": ["log_now", "start_journey"],
        "description": "CTA button text on the empty-state onboarding screen",
    },
}


def get_variant(user_id: int, experiment: str) -> str:
    """Return the variant this user is assigned to for *experiment*.

    Assignment is deterministic: same user + same experiment always returns
    the same variant (no DB required, no cookies).  Uses SHA-256 so the
    distribution is uniform.

    Args:
        user_id:    The authenticated user's integer ID.
        experiment: A key from the EXPERIMENTS registry.

    Returns:
        The assigned variant string, e.g. ``"control"`` or ``"treatment"``.
        Returns ``"control"`` if the experiment name is unknown.
    """
    if experiment not in EXPERIMENTS:
        logger.warning("Unknown A/B experiment: %s", experiment)
        return "control"

    meta = EXPERIMENTS[experiment]
    variants = meta["variants"]

    # Deterministic hash: SHA-256(user_id:experiment) → first 8 hex chars → int
    key = f"{user_id}:{experiment}"
    digest = hashlib.sha256(key.encode()).hexdigest()
    bucket = int(digest[:8], 16) % len(variants)
    return variants[bucket]


def log_conversion(user_id: int, experiment: str, event: str, variant: str | None = None) -> None:
    """Log a conversion event for offline analysis.

    Writes a structured JSON log line that can be scraped by any log
    aggregator (e.g. Better Stack, Logtail, Datadog free tier).

    Args:
        user_id:    The authenticated user's integer ID.
        experiment: The experiment name.
        event:      Conversion event label, e.g. ``"cta_click"`` or ``"log_submitted"``.
        variant:    Optional variant string; computed from user_id if omitted.
    """
    if variant is None:
        variant = get_variant(user_id, experiment)

    logger.info(
        "ab_conversion",
        extra={
            "event_type": "ab_conversion",
            "user_id": user_id,
            "experiment": experiment,
            "variant": variant,
            "conversion_event": event,
        },
    )


def get_all_variants(user_id: int) -> dict[str, str]:
    """Return a mapping of experiment → variant for all registered experiments.

    Useful for passing to templates so variant-specific UI can be rendered.

    Example::

        ab = get_all_variants(current_user.id)
        # {"suggestion_layout": "control", "dashboard_tip_position": "below_orb", ...}
    """
    return {exp: get_variant(user_id, exp) for exp in EXPERIMENTS}
