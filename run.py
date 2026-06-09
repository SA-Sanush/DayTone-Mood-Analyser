from app import create_app
from app.extensions import db


app = create_app()


@app.cli.command("init-db")
def init_db():
    """Create database tables."""
    db.create_all()
    print("DayTone database initialized.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
