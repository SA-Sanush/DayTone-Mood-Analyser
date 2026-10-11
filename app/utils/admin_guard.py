from app.models import User


def is_last_admin(user):
    """Return True if the given user is the last active admin of their specific role tier.

    Admin and Developer are treated as completely independent roles:
    - For a user with role='admin', check if they are the last remaining admin.
    - For a user with role='developer', check if they are the last remaining developer.
    A developer's existence does NOT count as an admin, and vice versa.
    """
    if user.role == "admin":
        count = User.query.filter(
            User.role == "admin",
            User.deleted_at.is_(None)
        ).count()
        return count <= 1

    if user.role == "developer":
        count = User.query.filter(
            User.role == "developer",
            User.deleted_at.is_(None)
        ).count()
        return count <= 1

    return False

