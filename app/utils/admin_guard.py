from app.models import User

def is_last_admin(user):
    """Check if the user is the last remaining active user with admin capabilities (admin or developer role)."""
    if user.role not in ("admin", "developer"):
        return False
    
    admin_count = User.query.filter(
        User.role.in_(["admin", "developer"]),
        User.deleted_at.is_(None)
    ).count()
    
    return admin_count <= 1
