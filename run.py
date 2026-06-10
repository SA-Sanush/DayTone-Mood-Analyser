import os

from app import create_app
from app.extensions import db


app = create_app()


@app.cli.command("init-db")
def init_db():
    """Create database tables."""
    db.create_all()
    print("DayTone database initialized.")


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
