from flask import Blueprint


mood_bp = Blueprint("mood", __name__)

from . import routes  # noqa: E402,F401
