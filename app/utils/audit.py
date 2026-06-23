"""Admin audit logging helper.

Call ``log_admin_action`` inside any admin route, then commit the session.
"""

from flask import request

from app.extensions import db
from app.models import AuditLog


def log_admin_action(
    admin_id: int,
    action: str,
    target_type: str | None = None,
    target_id: int | None = None,
    detail: str | None = None,
) -> AuditLog:
    """Record an admin action in the audit log.

    The caller **must** call ``db.session.commit()`` after this function —
    the entry is added to the session but not flushed automatically so that
    it can be rolled back together with the main action if needed.

    Args:
        admin_id:    ID of the admin performing the action.
        action:      Short action identifier, e.g. ``'delete_user'``.
        target_type: Model name of the affected object, e.g. ``'User'``.
        target_id:   Primary key of the affected object.
        detail:      Optional free-text or JSON string with extra context.

    Returns:
        The unsaved :class:`AuditLog` instance.
    """
    entry = AuditLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=request.remote_addr,
    )
    db.session.add(entry)
    return entry
