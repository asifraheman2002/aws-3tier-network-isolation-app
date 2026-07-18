import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)

# Enable CORS for frontend requests
CORS(app)

# ==========================
# Database Configuration
# ==========================
DB_HOST = os.environ.get("DB_HOST", "YOUR_RDS_ENDPOINT.amazonaws.com")
DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "YourSecurePassword123")
DB_NAME = os.environ.get("DB_NAME", "guestbook_db")


# ==========================
# Database Connection
# ==========================
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


# ==========================
# Initialize Database
# ==========================
def init_db():
    """Create database and table if they don't exist."""

    conn = None

    try:
        # Create database if it doesn't exist
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )

        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")

        conn.commit()

    finally:
        if conn:
            conn.close()

    conn = None

    try:
        # Create table
        conn = get_db_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        conn.commit()
        print("Database initialized successfully.")

    except Exception as e:
        print(f"Database Initialization Error: {e}")

    finally:
        if conn:
            conn.close()


# ==========================
# Health Check
# ==========================
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "tier": "application"
    }), 200


# ==========================
# Get Guestbook Entries
# ==========================
@app.route("/api/entries", methods=["GET"])
def get_entries():

    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    name,
                    message,
                    DATE_FORMAT(created_at,'%Y-%m-%d %H:%i') AS created_at
                FROM entries
                ORDER BY id DESC
            """)

            result = cursor.fetchall()

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()


# ==========================
# Add Guestbook Entry
# ==========================
@app.route("/api/entries", methods=["POST"])
def add_entry():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    name = data.get("name")
    message = data.get("message")

    if not name or not message:
        return jsonify({"error": "Name and message are required"}), 400

    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO entries (name, message)
                VALUES (%s, %s)
                """,
                (name, message)
            )

        conn.commit()

        return jsonify({
            "message": "Entry added successfully!"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conn:
            conn.close()


# ==========================
# Run Application
# ==========================
if __name__ == "__main__":

    # Wait for RDS to become available
    time.sleep(2)

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )