from flask import Flask
from models.db import db
from routes.auth_routes import auth_bp
from routes.listing_routes import listing_bp
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = 'loopback-secret-key-change-in-production'
# Respect a DATABASE_URL env var (e.g. for PostgreSQL) and fall back to a
# local SQLite DB for quick local development so the app can run without
# a running Postgres instance.
db_uri = os.environ.get('DATABASE_URL') or 'sqlite:///rewaste_dev.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max upload

# ── Initialize extensions ──────────────────────────────────────────────────────
db.init_app(app)

# ── Register blueprints ────────────────────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(listing_bp)

# ── Create tables on first run ─────────────────────────────────────────────────
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("The app will run but database features may not work.")

if __name__ == '__main__':
    app.run(debug=True)
