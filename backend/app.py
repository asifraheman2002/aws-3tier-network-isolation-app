import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

# ==========================
# Database Configuration
# ==========================

DB_HOST = os.environ.get(
    "DB_HOST",
    "database.cp8wwi4sas3e.ap-south-1.rds.amazonaws.com"
)

DB_USER = os.environ.get(
    "DB_USER",
    "admin"
)

DB_PASSWORD = os.environ.get(
    "DB_PASSWORD",
    "Admin-123"
)

DB_NAME = os.environ.get(
    "DB_NAME",
    "guestbook_db"
)

# ==========================
# Database Connection
# ==========================

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

# ==========================
# Initialize Database
# ==========================

def init_db():

    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True
    )

    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")

    conn.close()

    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

    conn.close()

    print("Database initialized successfully.")

# ==========================
# API Routes
# ==========================

@app.route("/api/entries", methods=["GET"])
def get_entries():

    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute("""
        SELECT
            id,
            name,
            message,
            created_at
        FROM entries
        ORDER BY id DESC
        """)

        rows = cursor.fetchall()

    conn.close()

    return jsonify(rows)


@app.route("/api/entries", methods=["POST"])
def add_entry():

    data = request.get_json()

    if not data:
        return jsonify({"error":"Invalid JSON"}),400

    name = data.get("name")
    message = data.get("message")

    if not name or not message:
        return jsonify({"error":"Name and Message required"}),400

    conn = get_db_connection()

    with conn.cursor() as cursor:

        cursor.execute("""
        INSERT INTO entries(name,message)
        VALUES(%s,%s)
        """,(name,message))

    conn.close()

    return jsonify({"message":"Entry added successfully"}),201


# ==========================
# Health Check
# ==========================

@app.route("/")
def health():
    return "Guestbook API Running"


# ==========================
# Main
# ==========================

if __name__ == "__main__":

    print("Initializing database...")
    time.sleep(2)

    init_db()

    print("Guestbook Application Started")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )