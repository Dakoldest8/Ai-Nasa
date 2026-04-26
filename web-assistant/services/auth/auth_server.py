from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import os
import hashlib
from pathlib import Path
from dotenv import load_dotenv

# Load env from project root and web-assistant folder (web-assistant overrides root)
THIS_FILE = Path(__file__).resolve()
ROOT_ENV = THIS_FILE.parents[3] / ".env"
WEB_ENV = THIS_FILE.parents[2] / ".env"
load_dotenv(ROOT_ENV)
load_dotenv(WEB_ENV, override=True)

app = Flask(__name__)

# MySQL Configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "nasa_ai_system")
DB_TABLE = os.getenv("DB_TABLE", "users")
DB_PORT = int(os.getenv("DB_PORT", 3306))


def get_db_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            autocommit=True
        )
        return connection
    except Error as e:
        print(f"[DB_ERROR] MySQL Connection Failed: {e}")
        return None


def _fetch_user(username: str):
    """Return (user_id, username, password_hash) or None."""
    try:
        connection = get_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor()
        query = f"SELECT user_id, username, password_hash FROM {DB_TABLE} WHERE username = %s"
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        return row
    except Error as e:
        print(f"[DB_ERROR] Fetch user failed: {e}")
        return None


@app.route("/login", methods=["POST"])
def login():
    """Validate username + password against MySQL (sha256 hashed)."""
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    row = _fetch_user(username)
    if not row:
        return jsonify({"status": "unauthorized"}), 401

    user_id, db_username, db_hash = row
    hashed = hashlib.sha256(password.encode()).hexdigest()
    if hashed == db_hash:
        # Return a stable numeric user_id so AI memory never mixes
        return jsonify({"status": "ok", "user_id": user_id, "username": db_username})

    return jsonify({"status": "unauthorized"}), 401


@app.route("/validate", methods=["POST"])
def validate_user():
    """Validate that a user exists (simple session checks)."""
    data = request.json or {}
    username = (data.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username required"}), 400

    row = _fetch_user(username)
    if row:
        user_id, db_username, _ = row
        return jsonify({"status": "ok", "user_id": user_id, "username": db_username})

    return jsonify({"status": "unauthorized"}), 401


@app.route("/health")
def health():
    try:
        connection = get_db_connection()
        if connection:
            connection.close()
            db_status = "connected"
        else:
            db_status = "failed"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "auth server running",
        "db": {
            "type": "MySQL",
            "host": DB_HOST,
            "database": DB_NAME,
            "table": DB_TABLE,
            "status": db_status
        }
    })


if __name__ == "__main__":
    app.run(port=7000, debug=True)
